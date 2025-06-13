# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Importer task and models."""

import uuid

from invenio_accounts.models import User
from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadataBase
from invenio_records_resources.records.models import FileRecordModelMixin
from sqlalchemy_utils.types import UUIDType


class ImporterTaskModel(db.Model, RecordMetadataBase):
    """Model for importer task."""

    __tablename__ = "importer_tasks_metadata"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id), index=True)
    bucket = db.relationship(Bucket, foreign_keys=[bucket_id])

    started_by_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="SET NULL"),
        nullable=True,
    )
    started_by = db.relationship(User)


class ImporterTaskFileModel(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """File associated with a importer task."""

    __record_model_cls__ = ImporterTaskModel
    __tablename__ = "importer_tasks_files"


class ImporterRecordModel(db.Model, RecordMetadataBase):
    """Model for importer record."""

    __tablename__ = "importer_records_metadata"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)

    task_id = db.Column(
        UUIDType, db.ForeignKey(ImporterTaskModel.id, ondelete="CASCADE")
    )
    task = db.relationship(ImporterTaskModel)
