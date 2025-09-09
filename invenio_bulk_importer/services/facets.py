# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Facet definitions."""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.records.facets import TermsFacet

from invenio_bulk_importer.services.states import ImporterRecordState, ImporterTaskState

task_status = TermsFacet(
    field="status",
    label=_("Status"),
    value_labels={
        ImporterTaskState.CREATED.value: _("Created"),
        ImporterTaskState.VALIDATING.value: _("Validating"),
        ImporterTaskState.VALIDATION_FAILED.value: _("Validated with failures"),
        ImporterTaskState.VALIDATED.value: _("Validated"),
        ImporterTaskState.IMPORTING.value: _("Importing"),
        ImporterTaskState.IMPORT_FAILED.value: _("Imported with failures"),
        ImporterTaskState.SUCCESS.value: _("Success"),
        ImporterTaskState.DAMAGED.value: _("Damaged"),
    },
)

record_type = TermsFacet(
    field="record_type",
    label=_("Record type"),
)

record_status = TermsFacet(
    field="status",
    label=_("Status"),
    value_labels={
        ImporterRecordState.CREATED.value: _("Created"),
        ImporterRecordState.VALIDATING.value: _("Validating"),
        ImporterRecordState.SERIALIZER_VALIDATION_FAILED.value: _(
            "Serializer validation failed"
        ),
        ImporterRecordState.VALIDATION_FAILED.value: _("Validation failed"),
        ImporterRecordState.VALIDATED.value: _("Validated"),
        ImporterRecordState.IMPORT_FAILED.value: _("Import failed"),
        ImporterRecordState.IMPORTED.value: _("Success"),
    },
)
