import os
import time
from io import BytesIO


def test_importer_task_with_create(
    running_app,
    db,
    admin_client,
    headers,
    minimal_importer_task,
    location,
    search_clear,
    community,
):
    """Test Importer Task APIs and the flow of creating, validating, and loading records."""
    task_id = None
    valid_record_id = None
    new_record_id = None

    # Get Record types
    with admin_client.get("/importer-tasks/config", headers=headers) as response:
        expected = ["record"]
        assert response.status_code == 200
        assert response.json == expected

    # Get Record Type config.
    with admin_client.get("/importer-tasks/config/record") as response:
        expected = {
            "serializers": ["csv"],
            "options": {"doi_minting": False, "publish": True},
        }
        assert response.status_code == 200
        assert response.json == expected

    # Create Importer Task.
    with admin_client.post(
        "/importer-tasks", headers=headers, json=minimal_importer_task
    ) as response:
        assert response.status_code == 201
        task_id = response.json["id"]
        assert response.json["record_type"] == "record"
        assert response.json["serializer"] == "csv"
        assert response.json["status"] == "created"

    # Add Metadata File to importer task.
    local_dir = os.path.dirname(__file__)
    file_path = os.path.join(f"{local_dir}/../data", "rdm_records.csv")
    # Read the file and create a BytesIO stream
    with open(file_path, "rb") as f:
        # Add metadata file to the importer task
        with admin_client.put(
            f"/importer-tasks/{task_id}/metadata",
            headers={
                **headers,
                "content-type": "application/octet-stream",
                "X-Filename": "rdm_records.csv",
            },
            data=BytesIO(f.read()),
        ) as response:
            assert response.status_code == 200
            response.json["size"] == 44663
            response.json["mimetype"] == "text/csv"

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
        assert response.json["versions"]["index"] == 1
        assert response.json["status"] == "published"
        assert response.json["files"]["entries"]["xml.xsd"]["size"] == 1663
        assert (
            response.json["parent"]["communities"]["entries"][0]["id"] == community.id
        )
