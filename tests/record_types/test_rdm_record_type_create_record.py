from flask_security import login_user
from invenio_accounts.proxies import current_datastore
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
    app, db, user_admin, validated_rdm_record_instance_with_community, search_clear
):
    """Test publishing a record with files into a community."""
    assert_counts(buckets=2, objs=2, fileinstances=2)
    record = validated_rdm_record_instance_with_community.run()
    RDMDraft.index.refresh()
    RDMRecord.index.refresh()
    assert record
    assert_counts(buckets=4, objs=6, fileinstances=6, drafts=1, records=1)
    all_records = current_rdm_records_service.search(user_admin.identity)
    hit = list(all_records.hits)[0]
    assert hit["id"] == record["id"]
    assert hit["parent"]["communities"]["entries"][0]["slug"] == "test-community"
    assert hit["is_published"]
    assert not hit["is_draft"]
    assert all_records.total == 1


def test_publish_record_with_files_with_no_community(
    app,
    set_app_config_fn_scoped,
    db,
    user_admin,
    validated_rdm_record_instance,
    search_clear,
):
    assert app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"]
    set_app_config_fn_scoped({"RDM_COMMUNITY_REQUIRED_TO_PUBLISH": False})
    assert not app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"]
    assert_counts(buckets=1, objs=2, fileinstances=2)
    record = validated_rdm_record_instance.run()
    RDMDraft.index.refresh()
    RDMRecord.index.refresh()
    assert record
    assert_counts(buckets=3, objs=6, fileinstances=6, drafts=1, records=1)
    all_records = current_rdm_records_service.search(user_admin.identity)
    hit = list(all_records.hits)[0]
    assert hit["id"] == record["id"]
    assert not hit["parent"]["communities"]
    assert hit["is_published"]
    assert not hit["is_draft"]
    assert all_records.total == 1


def test_publish_record_with_no_files_with_no_community(
    app,
    set_app_config_fn_scoped,
    db,
    user_admin,
    validated_rdm_record_instance_no_files,
    search_clear,
):
    assert app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"]
    set_app_config_fn_scoped({"RDM_COMMUNITY_REQUIRED_TO_PUBLISH": False})
    assert not app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"]
    assert_counts(buckets=1, objs=2, fileinstances=2)
    record = validated_rdm_record_instance_no_files.run()
    RDMDraft.index.refresh()
    RDMRecord.index.refresh()
    assert record
    assert_counts(buckets=3, objs=2, fileinstances=2, drafts=1, records=1)
    all_records = current_rdm_records_service.search(user_admin.identity)
    hit = list(all_records.hits)[0]
    assert hit["id"] == record["id"]
    assert not hit["parent"]["communities"]
    assert hit["is_published"]
    assert not hit["is_draft"]
    assert all_records.total == 1
