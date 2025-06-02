# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Rdm specific record resources."""

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_records_resources.tasks import system_identity
from marshmallow.exceptions import ValidationError as MarshmallowValidationError

from invenio_bulk_importer.errors import Error
from invenio_bulk_importer.record_types.base import (
    CommunityMixin,
    FileMixin,
    InvenioRecordMixin,
    RecordType,
)


class RDMRecord(CommunityMixin, FileMixin, InvenioRecordMixin, RecordType):
    """RDM Record validation and loading class."""

    def __init__(
        self,
        serializer_data: tuple[dict | None, dict | None],
        bucket_id: str = None,
        **kwargs,
    ):
        """Initialize the rdm record resource.

        Args:
            serializer_data (tuple[dict | None, dict | None]): Data from the serializer [serialized record dict, errors].
            bucket_id (str): Identifier for the invenio bucket of the Bulk Importer process.
            **kwargs: Additional keyword arguments.
        """
        # Initialize the serializer data and errors
        self._add_community_vars(serializer_data)
        self._add_file_vars(serializer_data, bucket_id)
        super().__init__(serializer_data)
        self.kwargs = kwargs

    def _verify_rdm_record_correctness(self, serializer_data):
        """Verify that the RDM record is correct."""
        schema = current_rdm_records_service.schema
        try:
            self._record = schema.load(
                serializer_data,
                context={"identity": system_identity},
                raise_errors=True,
            )
        except MarshmallowValidationError as e:
            self._process_validation_errors(e.messages, prefix="")

    def _process_validation_errors(self, errors, prefix=""):
        """Process validation errors recursively.

        Args:
            errors: The validation errors dict or list
            prefix: The current field path prefix
        """
        if isinstance(errors, dict):
            # Handle dictionary of errors (field_name -> error_message)
            for field, error in errors.items():
                field_path = f"{prefix}.{field}" if prefix else field

                if isinstance(error, (dict, list)):
                    # Recursively process nested errors
                    self._process_validation_errors(error, field_path)
                else:
                    # Handle string or list of string errors
                    if isinstance(error, list):
                        for err_msg in error:
                            self._add_error(
                                Error(type="validation_error", loc=prefix, msg=error)
                            )
                    else:
                        self._add_error(
                            Error(type="validation_error", loc=prefix, msg=error)
                        )
        elif isinstance(errors, list):
            # Handle list of errors
            if all(isinstance(item, (dict, list)) for item in errors):
                # List of nested structures
                for i, error in enumerate(errors):
                    self._process_validation_errors(error, f"{prefix}[{i}]")
            else:
                # List of string error messages
                for error in errors:
                    self._add_error(
                        Error(type="validation_error", loc=prefix, msg=error)
                    )

    def validate(self) -> bool:
        """Validate the serializer object can be loaded into Invenio.

        Returns True if the validation is successful, otherwise False.
        """
        if not self._serializer_record_data:
            self._add_error(
                Error(
                    type="serialized_record_not_provided",
                    loc="serialized_record",
                    msg="Existing serialized errors, cannot progress any further.",
                )
            )
            return False
        self._verify_record_exists(self.id)
        self._verify_files_accessible(self._files)
        self._verify_communities_exist(self._serializer_communities)
        self._verify_rdm_record_correctness(self._serializer_record_data)
        return self.is_succssful

    def run(self) -> dict:
        """Run the record creation process.

        Returns:
            dict: The created record.
        """
        pass
