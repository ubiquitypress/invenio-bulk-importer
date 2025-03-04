# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Bulk creation, import, and/or edittion of record and files for Invenio.."""

# TODO: This is an example file. Remove it if you do not need it, including
# the templates and static folders as well as the test case.

from flask import Blueprint, render_template
from invenio_i18n import gettext as _

blueprint = Blueprint(
    "invenio_bulk_importer",
    __name__,
    template_folder="templates",
    static_folder="static",
)


@blueprint.route("/")
def index():
    """Render a basic view."""
    return render_template(
        "invenio_bulk_importer/index.html",
        module_name=_("Invenio-Bulk-Importer"),
    )
