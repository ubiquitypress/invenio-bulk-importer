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
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.resources.records import RecordResourceConfig
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig

importer_task_error_handlers = RecordResourceConfig.error_handlers.copy()
importer_task_error_handlers.update(
    {
        FileNotFoundError: create_error_handler(
            HTTPJSONException(
                code=404,
                description="No file exists for this importer task.",
            )
        ),
        PIDDoesNotExistError: create_error_handler(
            HTTPJSONException(
                code=404,
                description="The persistent identifier does not exist.",
            )
        ),
    }
)


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

    error_handlers = FromConfig(
        "IMPORTER_TASK_ERROR_HANDLERS", default=importer_task_error_handlers
    )

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
