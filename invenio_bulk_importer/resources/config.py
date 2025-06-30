# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Config for Importer Task/Record Resource."""

import marshmallow as ma
from flask_resources import (
    BaseObjectSchema,
    HTTPJSONException,
    JSONSerializer,
    ResponseHandler,
    create_error_handler,
)
from invenio_i18n import gettext as _
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.files import FileResourceConfig
from invenio_records_resources.resources.records import RecordResourceConfig
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig

from invenio_bulk_importer.errors import ImporterTaskNoReadyError


class ImporterTaskResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Blueprint configuration."""

    blueprint_name = "importer-tasks"
    url_prefix = "/importer-tasks"

    routes = {
        "list": "",
        "item": "/<pid_value>",
        "metadata-file": "/<pid_value>/metadata",
        "item-record-list": "/<pid_value>/records",
        "config": "/config",
        "config-item": "/config/<record_type>",
        "item-validate": "/<pid_value>/validate",
        "item-load": "/<pid_value>/load",
        "item-status": "/<pid_value>/status",
    }

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
        ImporterTaskNoReadyError: create_error_handler(
            lambda e: HTTPJSONException(
                code=405,
                description=_("Importer Task in wrong status to proceed."),
            )
        ),
    }

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            BaseObjectSchema(), headers=etag_headers
        ),
    }

    request_view_args = {
        **RecordResourceConfig.request_view_args,
        "record_type": ma.fields.Str(),
    }


class ImporterTaskFilesResourceConfig(FileResourceConfig, ConfiguratorMixin):
    """Importer Task record files resource config."""

    allow_upload = True
    allow_archive_download = FromConfig("RDM_ARCHIVE_DOWNLOAD_ENABLED", True)
    blueprint_name = "files"
    url_prefix = "/importer-tasks/<pid_value>"

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
    }


class ImporterRecordResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Configuration for the Importer Record Resource."""

    blueprint_name = "importer-records"
    url_prefix = "/importer-records"

    routes = {
        "list": "",
        "item": "/<pid_value>",
        "run-item": "/<pid_value>/run",
    }

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            BaseObjectSchema(), headers=etag_headers
        ),
    }
