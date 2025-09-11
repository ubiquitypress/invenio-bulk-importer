from io import BytesIO

import pytest

from invenio_bulk_importer.proxies import (
    current_importer_records_service as records_service,
)
from invenio_bulk_importer.proxies import (
    current_importer_tasks_service as tasks_service,
)
from invenio_bulk_importer.records.api import ImporterRecord, ImporterTask
from invenio_bulk_importer.records.models import ImporterRecordModel, ImporterTaskModel


def test_create_importer_task(
    app, db, user_admin, minimal_importer_task, location, search_clear
):
    """Test creating an importer task with minimal data."""

    task = tasks_service.create(user_admin.identity, data=minimal_importer_task)
    task_data = task.data
    assert task_data["title"] == minimal_importer_task["title"]
    assert task_data["description"] == minimal_importer_task["description"]
    assert task_data["mode"] == minimal_importer_task["mode"]
    assert task_data["status"] == minimal_importer_task["status"]
    assert task_data["record_type"] == minimal_importer_task["record_type"]
    assert task_data["serializer"] == minimal_importer_task["serializer"]
    assert task_data["options"] == {
        "doi_minting": False,
        "publish": True,
    }
    # Check start_by_id is set from component running.
    task_model_instance = db.session.get(ImporterTaskModel, task.id)
    assert task_model_instance.started_by_id == int(user_admin.id)

    ImporterTask.index.refresh()

    # try to search for the profile
    all_tasks = tasks_service.search(user_admin.identity)
    assert all_tasks.total == 1
    hits = list(all_tasks.hits)
    assert hits[0] == task.data

    # Add metadata file to importer task.
    stream = BytesIO(b"csvdata")
    metadata_file_item = tasks_service.update_metadata_file(
        user_admin.identity,
        task.id,
        "new.csv",
        stream,
        content_length=stream.getbuffer().nbytes,
    )
    file_output = tasks_service.read_metadata_file(user_admin.identity, task.id)
    assert file_output
    file_deleted = tasks_service.delete_metadata_file(user_admin.identity, task.id)
    pytest.raises(
        FileNotFoundError,
        tasks_service.read_metadata_file,
        user_admin.identity,
        task.id,
    )


def test_starting_validation(app, db, user_admin, task, community, search_clear):
    """Test starting validation of an importer task."""
    # Start validation
    task_result = tasks_service.start_validation(user_admin.identity, task.id)
    assert task_result.data["status"] == "created"

    record_model_instances = (
        db.session.query(ImporterRecordModel)
        .filter(ImporterRecordModel.task_id == task.id)
        .all()
    )
    assert len(record_model_instances) == 3

    ImporterTask.index.refresh()
    ImporterRecord.index.refresh()

    # Assertions - there will be 3 records, one valid, the others fail at serializer or at record type validation.
    all_records = records_service.search(user_admin.identity)
    assert all_records.total == 3
    hits = list(all_records.hits)
    serializer_validation_failure_hits = [
        hit for hit in hits if hit["status"] == "serializer validation failed"
    ]
    invenio_validation_failure_hits = [
        hit for hit in hits if hit["status"] == "validation failed"
    ]
    validated_hits = [hit for hit in hits if hit["status"] == "validated"]
    assert len(serializer_validation_failure_hits) == 1
    assert len(invenio_validation_failure_hits) == 1
    assert len(validated_hits) == 1
    serializer_validation_failure = serializer_validation_failure_hits[0]
    assert serializer_validation_failure["src_data"]
    assert "serializer_data" not in serializer_validation_failure
    assert "transformed_data" not in serializer_validation_failure
    assert len(serializer_validation_failure["errors"]) == 3
    invenio_validation_failure = invenio_validation_failure_hits[0]
    assert invenio_validation_failure["src_data"]
    assert invenio_validation_failure["serializer_data"]
    assert "transformed_data" not in invenio_validation_failure
    assert len(invenio_validation_failure["errors"]) == 12

    invenio_validated = validated_hits[0]
    assert invenio_validated["src_data"]
    assert invenio_validated["serializer_data"]
    assert invenio_validated["transformed_data"]
    assert "errors" not in invenio_validated
    # Check update to task metadata has occurred.
    all_tasks = tasks_service.search(user_admin.identity)
    assert all_tasks.total == 1
    hits = list(all_tasks.hits)
    assert hits[0]["status"] == "validated with failures"
    assert hits[0]["records_status"] == {
        "serializer validation failed": 1,
        "total_records": 3,
        "validated": 1,
        "validation failed": 1,
    }
