# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Bulk creation, import, and/or edittion of record and files for Invenio.."""

from invenio_i18n import gettext as _

from . import config


class InvenioBulkImporter(object):
    """Invenio-Bulk-Importer extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        # TODO: This is an example of translation string with comment. Please
        # remove it.
        # NOTE: This is a note to a translator.
        _("A translation string")
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
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
