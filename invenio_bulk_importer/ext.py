# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Bulk creation, import, and/or edittion of record and files for Invenio.."""

from invenio_records_resources.services import FileService

from . import config
from .services.config import (
    ImporterRecordServiceConfig,
    ImporterTaskFileServiceConfig,
    ImporterTaskServiceConfig,
)
from .services.services import ImporterRecordService, ImporterTaskService


class InvenioBulkImporter(object):
    """Invenio-Bulk-Importer extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.tasks_service = None
        self.records_service = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
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
