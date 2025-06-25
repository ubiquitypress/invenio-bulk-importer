from invenio_files_rest.models import Bucket, FileInstance, ObjectVersion
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.records.models import RDMDraftMetadata, RDMRecordMetadata


def assert_counts(buckets=0, objs=0, fileinstances=0, drafts=0, records=0):
    """Helper to assert counts of file related tables."""
    assert Bucket.query.count() == buckets
    assert ObjectVersion.query.count() == objs
    assert FileInstance.query.count() == fileinstances
    assert RDMDraftMetadata.query.count() == drafts
    assert RDMRecordMetadata.query.count() == records


def test_publish_record_with_files_into_a_community(
    app, db, user_admin, validated_edit_rdm_record_instance_with_community, search_clear
):
    """Test publishing a record with files into a community."""
    assert_counts(buckets=4, objs=2, fileinstances=2, drafts=1, records=1)
    record = validated_edit_rdm_record_instance_with_community.run(mode="import")
    RDMDraft.index.refresh()
    RDMRecord.index.refresh()
    assert record
    assert_counts(buckets=6, objs=6, fileinstances=6, drafts=2, records=2)
    all_records = current_rdm_records_service.search(user_admin.identity)
    hit = list(all_records.hits)[0]
    assert hit["id"] == record["id"]
    assert hit["parent"]["communities"]["entries"][0]["slug"] == "test-community"
    assert hit["is_published"]
    assert not hit["is_draft"]
    assert hit["versions"]["index"] == 2
    assert hit["status"] == "published"
    assert all_records.total == 1


def test_publish_record_with_no_files_into_a_community(
    app,
    db,
    user_admin,
    validated_edit_rdm_record_instance_with_community_and_no_files,
    search_clear,
):
    """Test publishing a record with files into a community."""
    assert_counts(buckets=4, objs=2, fileinstances=2, drafts=1, records=1)
    current_record = current_rdm_records_service.read(
        user_admin.identity,
        validated_edit_rdm_record_instance_with_community_and_no_files._importer_record.get(
            "existing_record_id"
        ),
    )
    assert current_record.to_dict()["metadata"]["title"] == "Logan"
    record = validated_edit_rdm_record_instance_with_community_and_no_files.run(
        mode="import"
    )
    RDMDraft.index.refresh()
    RDMRecord.index.refresh()
    assert record
    assert_counts(buckets=4, objs=2, fileinstances=2, drafts=1, records=1)
    all_records = current_rdm_records_service.search(user_admin.identity)
    hit = list(all_records.hits)[0]
    assert record["id"] == current_record.id
    assert hit["id"] == record["id"]
    assert hit["parent"]["communities"]["entries"][0]["slug"] == "test-community"
    assert hit["metadata"]["title"] == "Micraster ernsti Schlüter 2024, sp. nov."
    assert hit["is_published"]
    assert not hit["is_draft"]
    assert hit["versions"]["index"] == 1
    assert hit["status"] == "published"
    assert all_records.total == 1
