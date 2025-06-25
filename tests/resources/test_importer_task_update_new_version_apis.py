import time


def test_importer_task_with_file_update_new_version(
    running_app,
    db,
    admin_client,
    headers,
    location,
    search_clear,
    community,
    edit_version_task,
):
    """Test Importer Task APIs and the flow of creating, validating, and loading records."""
    task_id = edit_version_task.id
    valid_record_id = None
    new_record_id = None

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
            "total_records": 3,
            "validation failed": 1,
            "serializer validation failed": 1,
        }

    # Get Importer Records
    time.sleep(6)  # Wait for the task to process
    with admin_client.get(
        f"/importer-records",
        headers=headers,
    ) as response:
        assert response.status_code == 200
        assert response.json["hits"]["total"] == 3

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
        new_record_id = response.json["generated_record_id"]
    assert new_record_id is not None, "No new record ID found"

    # Get the new record.
    with admin_client.get(
        f"/records/{new_record_id}",
        headers={
            "content-type": "application/json",
            "accept": "application/vnd.inveniordm.v1+json",
        },
    ) as response:
        assert response.status_code == 200
        assert response.json["id"] == new_record_id
        assert response.json["is_draft"] == False
        assert response.json["is_published"] == True
        assert (
            response.json["metadata"]["title"]
            == "Micraster ernsti Schlüter 2024, sp. nov."
        )
        assert response.json["versions"]["index"] == 2
        assert response.json["revision_id"] == 4
        assert response.json["status"] == "published"
        assert response.json["files"]["entries"]["xml.xsd"]["size"] == 1663
        assert (
            response.json["parent"]["communities"]["entries"][0]["id"] == community.id
        )
