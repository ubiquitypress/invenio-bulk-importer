# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Bulk creation, import, and/or edittion of record and files for Invenio.."""

from invenio_i18n import lazy_gettext as _

from invenio_bulk_importer.record_types.rdm import RDMRecord
from invenio_bulk_importer.serializers.records.csv import CSVRDMRecordSerializer

# TODO: This is an example file. Remove it if your package does not use any
# extra configuration variables.

BULK_IMPORTER_DEFAULT_VALUE = "foobar"
"""Default value for the application."""

BULK_IMPORTER_BASE_TEMPLATE = "invenio_bulk_importer/base.html"
"""Default base template for the demo page."""

BULK_IMPORTER_CUSTOM_FIELDS = {}
"""Custom fields for the importer."""

BULK_IMPORTER_RECORD_TYPES = {
    "record": {
        "class": RDMRecord,
        "options": {
            "doi_minting": False,
            "publish": True,
        },
        "serializers": {"csv": CSVRDMRecordSerializer},
    }
}
"""List of options and serializers to be used by the importer."""


#
# Importer tasks Search configuration
#
BULK_IMPORTER_TASKS_FACETS = {}

BULK_IMPORTER_TASKS_SORT_OPTIONS = {
    "bestmatch": dict(
        title=_("Best match"),
        fields=["_score"],  # ES defaults to desc on `_score` field
    ),
    "newest": dict(
        title=_("Newest"),
        fields=["-created"],
    ),
    "oldest": dict(
        title=_("Oldest"),
        fields=["created"],
    ),
}

BULK_IMPORTER_TASKS_SEARCH = {
    "facets": [],
    "sort": ["bestmatch", "newest", "oldest"],
}


#
# Importer records Search configuration
#
BULK_IMPORTER_RECORDS_FACETS = {}

BULK_IMPORTER_RECORDS_SORT_OPTIONS = {
    "bestmatch": dict(
        title=_("Best match"),
        fields=["_score"],  # ES defaults to desc on `_score` field
    ),
    "newest": dict(
        title=_("Newest"),
        fields=["-created"],
    ),
    "oldest": dict(
        title=_("Oldest"),
        fields=["created"],
    ),
}

BULK_IMPORTER_RECORDS_SEARCH = {
    "facets": [],
    "sort": ["bestmatch", "newest", "oldest"],
}
