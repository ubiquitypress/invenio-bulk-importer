from invenio_bulk_importer.services.states import ImporterRecordState, ImporterTaskState


def test_importer_task_states():
    """Test the ImporterTaskState and ImporterRecordState enums."""
    # Test ImporterRecordState enum
    assert ImporterRecordState.CREATED.value == "created"
    assert ImporterRecordState.VALIDATING.value == "validating"
    assert (
        ImporterRecordState.SERIALIZER_VALIDATION_FAILED.value
        == "serializer validation failed"
    )
    assert ImporterRecordState.VALIDATION_FAILED.value == "validation failed"
    assert ImporterRecordState.VALIDATED.value == "validated"
    assert ImporterRecordState.IMPORT_FAILED.value == "import failed"
    assert ImporterRecordState.IMPORTED.value == "success"

    # Test ImporterTaskState enum
    assert ImporterTaskState.CREATED.value == "created"
    assert ImporterTaskState.VALIDATING.value == "validating"
    assert ImporterTaskState.VALIDATION_FAILED.value == "validated with failures"
    assert ImporterTaskState.IMPORTING.value == "importing"
    assert ImporterTaskState.IMPORT_FAILED.value == "imported with failures"
    assert ImporterTaskState.SUCCESS.value == "success"
    assert ImporterTaskState.DAMAGED.value == "damaged"


def test_calculate_task_state():
    """Test the TaskStateCalculator.calculate_task_state method."""
    from invenio_bulk_importer.services.states import TaskStateCalculator

    # Test with no records
    record_states = {"total_records": 0}
    assert (
        TaskStateCalculator.calculate_task_state(record_states)
        == ImporterTaskState.CREATED.value
    )

    # Test with all created records
    record_states = {
        "total_records": 3,
        "created": 3,
    }
    assert (
        TaskStateCalculator.calculate_task_state(record_states)
        == ImporterTaskState.CREATED.value
    )

    # Still Created
    record_states = {
        "total_records": 5,
        "created": 5,
    }
    assert (
        TaskStateCalculator.calculate_task_state(record_states)
        == ImporterTaskState.CREATED.value
    )

    # Test with validating
    record_states = {
        "total_records": 5,
        "created": 2,
        "serializer validation failed": 1,
        "validation failed": 1,
        "validated": 1,
    }
    assert (
        TaskStateCalculator.calculate_task_state(record_states)
        == ImporterTaskState.VALIDATING.value
    )

    # Test with validating failed
    record_states = {
        "total_records": 5,
        "serializer validation failed": 1,
        "validation failed": 1,
        "validated": 3,
    }
    assert (
        TaskStateCalculator.calculate_task_state(record_states)
        == ImporterTaskState.VALIDATION_FAILED.value
    )

    # Test with all validated records
    record_states = {
        "total_records": 5,
        "validated": 5,
    }
    assert (
        TaskStateCalculator.calculate_task_state(record_states)
        == ImporterTaskState.VALIDATED.value
    )

    # Test for importing
    record_states = {
        "total_records": 5,
        "validated": 4,
        "success": 1,
    }
    assert (
        TaskStateCalculator.calculate_task_state(record_states)
        == ImporterTaskState.IMPORTING.value
    )

    # Test with importing failed
    record_states = {
        "total_records": 5,
        "import failed": 3,
        "success": 1,
    }
    assert (
        TaskStateCalculator.calculate_task_state(record_states)
        == ImporterTaskState.IMPORT_FAILED.value
    )

    # Test with success
    record_states = {
        "total_records": 5,
        "success": 5,
    }
    assert (
        TaskStateCalculator.calculate_task_state(record_states)
        == ImporterTaskState.SUCCESS.value
    )
