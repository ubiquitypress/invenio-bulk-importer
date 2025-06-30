# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""API views for Invenio Bulk Importer."""

from flask import Blueprint

blueprint = Blueprint(
    "invenio_bulk_importer_ext",
    __name__,
    template_folder="../templates",
)


def create_tasks_bp(app):
    """Creates a blueprint for the bulk importer tasks resource."""
    blueprint = app.extensions["invenio-bulk-importer"].tasks_resource.as_blueprint()
    return blueprint


def create_records_bp(app):
    """Creates a blueprint for the bulk importer records resource."""
    blueprint = app.extensions["invenio-bulk-importer"].records_resource.as_blueprint()
    return blueprint


def create_task_files_bp(app):
    """Create importer task files blueprint."""
    return app.extensions["invenio-bulk-importer"].task_files_resource.as_blueprint()
