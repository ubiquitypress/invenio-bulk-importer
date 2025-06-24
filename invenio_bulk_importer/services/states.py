# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""States for Importer Records and Tasks."""

from enum import Enum
from typing import Dict


class ImporterRecordState(Enum):
    """States for individual importer records."""

    CREATED = "created"
    VALIDATING = "validating"
    SERIALIZER_VALIDATION_FAILED = "serializer validation failed"
    VALIDATION_FAILED = "validation failed"
    VALIDATED = "validated"
    IMPORTING = "importing"
    IMPORT_FAILED = "import failed"
    SUCCESS = "success"


class ImporterTaskState(Enum):
    """States for importer tasks."""

    CREATED = "created"
    VALIDATING = "validating"
    VALIDATION_FAILED = "validated with failures"
    IMPORTING = "importing"
    IMPORT_FAILED = "imported with failures"
    SUCCESS = "success"


class TaskStateCalculator:
    """Calculate task state based on record states."""

    @staticmethod
    def calculate_task_state(record_states: Dict[str, int]) -> str:
        """
        Calculate task state based on record state counts.

        Args:
            record_states: Dictionary with state names as keys and counts as values

        Returns:
            Task state string
        """
        total_records = record_states["total_records"]

        if total_records == 0:
            return ImporterTaskState.CREATED.value

        # Check if all records are successful
        success_count = record_states.get(ImporterRecordState.SUCCESS.value, 0)
        if success_count == total_records:
            return ImporterTaskState.SUCCESS.value

        # Check if any records are still validating
        validating_count = record_states.get(ImporterRecordState.VALIDATING.value, 0)
        created_count = record_states.get(ImporterRecordState.CREATED.value, 0)
        if validating_count > 0 or created_count > 0:
            return ImporterTaskState.VALIDATING.value

        # Check if any records are validated (ready to run)
        validated_count = record_states.get(ImporterRecordState.VALIDATED.value, 0)
        if validated_count > 0:
            return ImporterTaskState.RUNNING.value

        # Check for validation failures
        validation_failed = record_states.get(
            ImporterRecordState.VALIDATION_FAILED.value, 0
        )
        serializer_failed = record_states.get(
            ImporterRecordState.SERIALIZER_VALIDATION_FAILED.value, 0
        )
        if validation_failed > 0 or serializer_failed > 0:
            if success_count > 0:
                return ImporterTaskState.WARNINGS.value
            else:
                return ImporterTaskState.VALIDATION_FAILED.value

        # Check for creation failures
        import_failed = record_states.get(ImporterRecordState.IMPORT_FAILED.value, 0)
        if import_failed > 0:
            if success_count > 0:
                return ImporterTaskState.WARNINGS.value
            else:
                return ImporterTaskState.FAILURE.value

        # Default fallback
        return ImporterTaskState.CREATED.value
