# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Bulk creation, import, and/or edittion of record and files for Invenio."""

from invenio_records_resources.resources.files import FileResource
from invenio_records_resources.services import FileService

from . import config
from .resources import (
    ImporterRecordResource,
    ImporterRecordResourceConfig,
    ImporterTaskFilesResourceConfig,
    ImporterTaskResource,
    ImporterTaskResourceConfig,
)
from .services import (
    ImporterRecordService,
    ImporterRecordServiceConfig,
    ImporterTaskFileServiceConfig,
    ImporterTaskService,
    ImporterTaskServiceConfig,
)


class InvenioBulkImporter(object):
    """Invenio-Bulk-Importer extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.tasks_service = None
        self.records_service = None
        self.records_resource = None
        self.tasks_resource = None
        self.task_files_resource = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
        self.init_resources(app)
        app.extensions["invenio-bulk-importer"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed
        if "BASE_TEMPLATE" in app.config:
            app.config.setdefault(
                "BULK_IMPORTER_BASE_TEMPLATE",
                app.config["BASE_TEMPLATE"],
            )
        for k in dir(config):
            if k.startswith("BULK_IMPORTER_"):
                app.config.setdefault(k, getattr(config, k))

    def init_services(self, app):
        """Init services."""
        self.tasks_service = ImporterTaskService(
            config=ImporterTaskServiceConfig.build(app),
            files_service=FileService(ImporterTaskFileServiceConfig.build(app)),
        )
        self.records_service = ImporterRecordService(
            config=ImporterRecordServiceConfig.build(app),
        )

    def init_resources(self, app):
        """Initialize resources."""
        self.tasks_resource = ImporterTaskResource(
            config=ImporterTaskResourceConfig.build(app),
            service=self.tasks_service,
        )
        # Im,porter Task files resource
        self.task_files_resource = FileResource(
            service=self.tasks_service.files,
            config=ImporterTaskFilesResourceConfig.build(app),
        )
        self.records_resource = ImporterRecordResource(
            config=ImporterRecordResourceConfig.build(app),
            service=self.records_service,
        )


def api_finalize_app(app):
    """Finalize app for api."""
    init(app)


def init(app):
    """Register services in the service registry."""
    ext = app.extensions["invenio-bulk-importer"]

    # Get the service registry
    sregistry = app.extensions["invenio-records-resources"].registry

    # Register the main task service
    sregistry.register(
        ext.tasks_service, service_id=ext.tasks_service.config.service_id
    )

    # Register the task files service
    sregistry.register(
        ext.tasks_service.files,
        service_id=ext.tasks_service.files.config.service_id,
    )

    # Register the records service
    sregistry.register(
        ext.records_service, service_id=ext.records_service.config.service_id
    )

    # Register indexers if you have them
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(
        ext.tasks_service.indexer,
        indexer_id=ext.tasks_service.config.service_id,
    )
    iregistry.register(
        ext.records_service.indexer,
        indexer_id=ext.records_service.config.service_id,
    )
