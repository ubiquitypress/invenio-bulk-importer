# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Bulk Importer Services."""
import os
from copy import deepcopy

from invenio_records_resources.services.records import RecordService
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    unit_of_work,
)

from .tasks import load_importer_file, run_transformed_record


class BulkImporterMixin:
    """Mixin for bulk importer services."""

    def get_current_task_data(self, record):
        """Get the current data of the importer task."""
        keys = ["uuid", "version_id", "indexed_at"]
        keys.extend(self.additional_keys)

        update_data = deepcopy(record.dumps())
        for key in keys:
            update_data.pop(key)
        return update_data


class ImporterTaskService(BulkImporterMixin, RecordService):
    """Importer Task Service class."""

    additional_keys = ["started_by", "started_by_id"]

    def __init__(self, config, files_service=None):
        """Constructor for RecordService."""
        super().__init__(config)
        self._files = files_service

    #
    # Subservices
    #
    @property
    def files(self):
        """Record files service."""
        return self._files

    def read_metadata_file(self, identity, id_):
        """Read the importer task metadata file."""
        return self._read_file(identity, "metadata", id_)

    @unit_of_work()
    def update_metadata_file(
        self, identity, id_, filename, stream, content_length=None, uow=None
    ):
        """Update the importer task metadata file."""
        # get the file extesion from filename
        extension = self._get_file_extension(filename)
        return self._update_file(identity, id_, stream, "metadata", extension, uow=uow)

    @unit_of_work()
    def delete_metadata_file(self, identity, id_, uow=None):
        """Delete the importer task metadata file."""
        return self._delete_file(identity, id_, "metadata", uow=uow)

    @unit_of_work()
    def start_validation(self, identity, id_, uow=None):
        """Load importer metadata for a record type using a specific serializer."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "read", record=record)
        # TODO: Validate Metadata file exists - throw error

        # Load the importer records with the specified serializer data.
        load_importer_file.delay(str(record.id))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
        )

    #
    # Private methods
    #
    def _update_task_metadata(self, identity, record, update_data, uow):
        """Update the importer task metadata, but not from form data."""
        data, _ = self.schema.load(
            update_data, context=dict(identity=identity, pid=record.pid, record=record)
        )
        # Run components
        self.run_components(
            "update",
            identity,
            data=data,
            record=record,
            uow=uow,
        )
        # Persist record (DB and index)
        uow.register(RecordCommitOp(record, self.indexer))

    def _get_file_extension(self, filename):
        """Get the file extension from the filename."""
        extension = None
        if filename:
            _, extension = os.path.splitext(filename)
        return extension

    def _find_file_in_record(self, file_name, record):
        """Find the file in the record."""
        full_file_name = None
        for key in record.files.keys():
            prefix_to_check = f"{file_name}."
            if key.startswith(prefix_to_check):
                full_file_name = key
                break
        return full_file_name

    def _read_file(self, identity, file_name, id_):
        """Read the importer task's file."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "read", record=record)
        full_file_name = self._find_file_in_record(file_name, record)
        record_file = record.files.get(full_file_name)
        if record_file is None:
            raise FileNotFoundError()
        return self.files.file_result_item(
            self.files,
            identity,
            record_file,
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )

    @unit_of_work()
    def _update_file(self, identity, id_, stream, file_name, file_extension, uow=None):
        """Update a importer task's file."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "update", record=record)

        full_file_name = f"{file_name}{file_extension}" if file_extension else file_name
        if (
            record.files
            and full_file_name not in record.files
            and self._find_file_in_record(file_name, record)
        ):
            # Delete the old file of a different extension
            self._delete_file(identity, id_, file_name, uow=uow)
        record.files[full_file_name] = stream
        uow.register(RecordCommitOp(record))

        return self.files.file_result_item(
            self.files,
            identity,
            record.files[full_file_name],
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )

    def _delete_file(self, identity, id_, file_name, uow=None):
        """Delete a importer task's file."""
        record = self.record_cls.pid.resolve(id_)
        # update permission on community is required to be able to remove file.
        self.require_permission(identity, "update", record=record)

        full_file_name = self._find_file_in_record(file_name, record)
        deleted_file = record.files.pop(full_file_name, None)
        if deleted_file is None:
            raise FileNotFoundError()

        deleted_file.delete(force=True)

        uow.register(RecordCommitOp(record))

        return self.files.file_result_item(
            self.files,
            identity,
            deleted_file,
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )


class ImporterRecordService(BulkImporterMixin, RecordService):
    """Importer Task Service class."""

    additional_keys = ["task_id"]

    @unit_of_work()
    def create(self, identity, data, task_id, uow=None, expand=False):
        """Create a record.

        :param identity: Identity of user creating the record.
        :param data: Input data according to the data schema.
        """
        return self._create(
            self.record_cls, identity, data, task_id, uow=uow, expand=expand
        )

    @unit_of_work()
    def _create(
        self,
        record_cls,
        identity,
        data,
        task_id,
        raise_errors=True,
        uow=None,
        expand=False,
    ):
        """Create a record.

        :param identity: Identity of user creating the record.
        :param dict data: Input data according to the data schema.
        :param bool raise_errors: raise schema ValidationError or not.
        """
        self.require_permission(identity, "create")

        # Validate data and create record with pid
        data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,  # if False, flow is continued with data
            # only containing valid data, but errors
            # are reported (as warnings)
        )

        # It's the components who saves the actual data in the record.
        record = record_cls.create({})

        # Run components
        self.run_components(
            "create",
            identity,
            data=data,
            record=record,
            errors=errors,
            uow=uow,
            task_id=task_id,
        )

        # Persist record (DB and index)
        uow.register(RecordCommitOp(record, self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            nested_links_item=getattr(self.config, "nested_links_item", None),
            errors=errors,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def start_run(self, identity, id_, uow=None):
        """Start the run of the importer record to create a new invenio record."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "read", record=record)
        # TODO: Validate Metadata file exists - throw error

        # Load the importer records with the specified serializer data.
        run_transformed_record.delay(str(record.id), str(record.task_id))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
        )
