from invenio_bulk_importer.records.models import ImporterTaskModel


def test_db_create(app, db, minimal_importer_task, user_admin):
    task = ImporterTaskModel(json=minimal_importer_task, started_by_id=user_admin.id)
    db.session.add(task)
    db.session.commit()
    task_id = task.id
    created_task = ImporterTaskModel.query.get(task_id)
    assert task_id is not None
    assert created_task.json == minimal_importer_task
    assert created_task.started_by_id == int(user_admin.id)
