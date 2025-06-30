# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Employee Profile service configuration."""
from invenio_records_resources.services import FileLink, FileServiceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_records_resources.services.records import RecordServiceConfig
from invenio_records_resources.services.records.components import DataComponent

from ..records.api import ImporterRecord, ImporterTask
from .components import ImporterRecordServiceComponent, ImporterTaskServiceComponent
from .links import ILink
from .permissions import ImporterRecordPermissionPolicy, ImporterTaskPermissionPolicy
from .schemas import ImporterRecordSchema, ImporterTaskSchema


class ImporterTaskServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Importer Task Service configuration Class."""

    service_id = "importertasks"

    # Record specific configuration
    record_cls = ImporterTask

    # Service schema
    schema = ImporterTaskSchema

    # Common configuration
    permission_policy_cls = ImporterTaskPermissionPolicy
    indexer_queue_name = "importertasks"

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

    service_id = "importertaskfiles"

    permission_policy_cls = ImporterTaskPermissionPolicy

    record_cls = ImporterTask

    file_links_item = {
        "self": FileLink("{+api}/importer-tasks/{id}/{+key}"),
    }


class ImporterRecordServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Importer Task Service configuration Class."""

    service_id = "importerrecords"

    # Record specific configuration
    record_cls = ImporterRecord

    # Service schema
    schema = ImporterRecordSchema

    # Common configuration
    permission_policy_cls = ImporterRecordPermissionPolicy
    indexer_queue_name = "importerrecords"

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
