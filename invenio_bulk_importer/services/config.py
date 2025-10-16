# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Importer service configuration."""

from invenio_records_resources.services import FileLink, FileServiceConfig
from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    FromConfigSearchOptions,
    SearchOptionsMixin,
)
from invenio_records_resources.services.records import RecordServiceConfig
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.config import (
    SearchOptions as SearchOptionsBase,
)
from invenio_records_resources.services.records.params import (
    FacetsParam,
    PaginationParam,
    QueryStrParam,
    SortParam,
)

from invenio_bulk_importer.services import facets

from ..records.api import ImporterRecord, ImporterTask
from .components import ImporterRecordServiceComponent, ImporterTaskServiceComponent
from .links import ILink
from .permissions import ImporterRecordPermissionPolicy, ImporterTaskPermissionPolicy
from .schemas import ImporterRecordSchema, ImporterTaskSchema


class ImporterTaskSearchOptions(SearchOptionsBase, SearchOptionsMixin):
    """Search options."""

    facets = {"status": facets.task_status, "record_type": facets.record_type}
    params_interpreters_cls = [
        QueryStrParam,
        PaginationParam,
        SortParam,
        FacetsParam,
    ]


class ImporterTaskServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Importer Task Service configuration Class."""

    service_id = "importer-tasks"

    # Record specific configuration
    record_cls = ImporterTask

    # Search configuration
    search = FromConfigSearchOptions(
        "BULK_IMPORTER_TASKS_SEARCH",
        "BULK_IMPORTER_TASKS_SORT_OPTIONS",
        "BULK_IMPORTER_TASKS_FACETS",
        search_option_cls=ImporterTaskSearchOptions,
    )

    # Service schema
    schema = ImporterTaskSchema

    # Common configuration
    permission_policy_cls = ImporterTaskPermissionPolicy
    indexer_queue_name = service_id

    components = [
        DataComponent,
        ImporterTaskServiceComponent,
    ]

    links_item = {
        "self": ILink("{+api}/importer-tasks/{id}"),
        "self_html": ILink("{+ui}/importer-tasks/{id}"),
        "edit_html": ILink("{+ui}/importer-tasks/{id}/edit"),
        "metadata": ILink("{+api}/importer-tasks/{id}/metadata"),
    }


class ImporterTaskFileServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Importer task file record service config."""

    service_id = "importer-task-files"

    permission_policy_cls = ImporterTaskPermissionPolicy

    record_cls = ImporterTask

    file_links_item = {
        "self": FileLink("{+api}/importer-tasks/{id}/{+key}"),
    }


class ImporterRecordSearchOptions(SearchOptionsBase, SearchOptionsMixin):
    """Search options."""

    facets = {"status": facets.record_status}
    params_interpreters_cls = [
        QueryStrParam,
        PaginationParam,
        SortParam,
        FacetsParam,
    ]


class ImporterRecordServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Importer Task Service configuration Class."""

    service_id = "importer-records"

    # Record specific configuration
    record_cls = ImporterRecord

    # Search configuration
    search = FromConfigSearchOptions(
        "BULK_IMPORTER_RECORDS_SEARCH",
        "BULK_IMPORTER_RECORDS_SORT_OPTIONS",
        "BULK_IMPORTER_RECORDS_FACETS",
        search_option_cls=ImporterRecordSearchOptions,
    )
    # Service schema
    schema = ImporterRecordSchema

    # Common configuration
    permission_policy_cls = ImporterRecordPermissionPolicy
    indexer_queue_name = service_id

    components = [
        DataComponent,
        ImporterRecordServiceComponent,
    ]

    links_item = {
        "self": ILink("{+api}/importer-records/{id}"),
        "self_html": ILink("{+ui}/importer-records/{id}"),
        "edit_html": ILink("{+ui}/importer-records/{id}/edit"),
        "metadata": ILink("{+api}/importer-records/{id}/metadata"),
    }
