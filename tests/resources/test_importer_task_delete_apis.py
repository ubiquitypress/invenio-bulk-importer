from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMRecord as InvenioRDMRecord

from invenio_bulk_importer.records.api import ImporterRecord, ImporterTask


def test_importer_task_with_file_update_new_version(
    running_app,
    db,
    user_admin,
    admin_client,
    headers,
    location,
    search_clear,
    delete_task,
):
    """Test Importer Task APIs and the flow of creating, validating, and loading records."""
    task_id = delete_task.id
    valid_record_id = None
    # Check record search
    all_records = current_rdm_records_service.search(user_admin.identity)
    assert all_records.total == 1
    # Start Validation of csv file
    with admin_client.post(
        f"/importer-tasks/{task_id}/validate",
        headers=headers,
        json={},
    ) as response:
        assert response.status_code == 200

    # Read Importer Task
    with admin_client.get(
        f"/importer-tasks/{task_id}",
        headers=headers,
    ) as response:
        assert response.status_code == 200
        assert response.json["records_status"] == {
            "validated": 1,
            "total_records": 1,
        }

    ImporterTask.index.refresh()
    ImporterRecord.index.refresh()

    # Get Importer Records
    with admin_client.get(
        "/importer-records",
        headers=headers,
    ) as response:
        assert response.status_code == 200
        assert response.json["hits"]["total"] == 1

        for hit in response.json["hits"]["hits"]:
            if hit["status"] == "validated":
                valid_record_id = hit["id"]
    assert valid_record_id is not None, "No validated record found"

    # Trigger Importer Records loading.
    with admin_client.post(
        f"/importer-records/{valid_record_id}/run",
        headers=headers,
    ) as response:
        assert response.status_code == 200

    # Read the validated record
    with admin_client.get(
        f"/importer-records/{valid_record_id}",
        headers=headers,
    ) as response:
        deleted_record_id = response.json["existing_record_id"]
    assert deleted_record_id is not None, "No new record ID found"
    # Get the new record.
    with admin_client.get(
        f"/records/{deleted_record_id}",
        headers={
            "content-type": "application/json",
            "accept": "application/vnd.inveniordm.v1+json",
        },
    ) as response:
        assert response.status_code == 410
        assert response.json["message"] == "Record deleted"
        assert response.json["tombstone"]["note"] == "Mistakenly imported"
    # Check record search
    InvenioRDMRecord.index.refresh()
    all_records = current_rdm_records_service.search(user_admin.identity)
    assert all_records.total == 0
