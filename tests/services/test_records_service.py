import time
import uuid

from invenio_files_rest.models import Bucket, FileInstance, ObjectVersion
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.records.models import RDMDraftMetadata, RDMRecordMetadata

from invenio_bulk_importer.proxies import current_importer_records_service
from invenio_bulk_importer.records.api import ImporterRecord
from invenio_bulk_importer.records.models import ImporterRecordModel


def assert_counts(buckets=0, objs=0, fileinstances=0, drafts=0, records=0):
    """Helper to assert counts of file related tables."""
    assert Bucket.query.count() == buckets
    assert ObjectVersion.query.count() == objs
    assert FileInstance.query.count() == fileinstances
    assert RDMDraftMetadata.query.count() == drafts
    assert RDMRecordMetadata.query.count() == records


def test_create_importer_record(
    app, db, user_admin, task, minimal_importer_record, location, search_clear
):
    """Test creating an importer task with minimal data."""
    record = current_importer_records_service.create(
        user_admin.identity, data=minimal_importer_record, task_id=task.id
    )
    record_data = record.data
    assert record_data["status"] == minimal_importer_record["status"]
    assert record_data["message"] == minimal_importer_record["message"]
    assert record_data["src_data"] == minimal_importer_record["src_data"]
    assert record_data["errors"] == minimal_importer_record["errors"]
    assert record_data["serializer_data"] == minimal_importer_record["serializer_data"]
    assert (
        record_data["transformed_data"] == minimal_importer_record["transformed_data"]
    )
    # Check start_by_id is set from component running.
    record_model_instance = db.session.get(ImporterRecordModel, record.id)
    assert record_model_instance.task_id == uuid.UUID(task.id)

    ImporterRecord.index.refresh()

    # try to search for the profile
    all_records = current_importer_records_service.search(user_admin.identity)
    assert all_records.total == 1
    hits = list(all_records.hits)
    assert hits[0] == record_data


def test_run_transformed_record(
    app, db, user_admin, validated_ir_instance_no_files_one_community, search_clear
):
    assert_counts(buckets=2, objs=2, fileinstances=2)
    record_item = current_importer_records_service.start_run(
        user_admin.identity, id_=validated_ir_instance_no_files_one_community.id
    )
    # Wait for 3 seconds
    time.sleep(3)
    RDMDraft.index.refresh()
    RDMRecord.index.refresh()
    ImporterRecord.index.refresh()
    # try to search for the profile
    all_importer_records = current_importer_records_service.search(user_admin.identity)
    assert all_importer_records.total == 1
    ir_hit = list(all_importer_records.hits)[0]
    assert record_item
    assert_counts(buckets=4, objs=2, fileinstances=2, drafts=1, records=1)
    all_records = current_rdm_records_service.search(user_admin.identity)
    hit = list(all_records.hits)[0]
    assert all_records.total == 1
    assert hit["is_published"]
    assert not hit["is_draft"]
    assert hit["id"] == ir_hit["generated_record_id"]
    assert ir_hit["status"] == "success"
