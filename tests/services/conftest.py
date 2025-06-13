# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Fixtures for testing Invenio RDM Record resources."""

import pytest


@pytest.fixture()
def minimal_importer_record():
    """Minimal importer task data."""
    return {
        "status": "created",
        "message": "This is a test importer task.",
        "src_data": {},
        "errors": [
            {
                "loc": "field1",
                "msg": "Field1 is required.",
                "type": "value_error.missing",
            }
        ],
        "serializer_data": {
            "title": "Test Importer Record",
            "description": "This is a test importer record.",
            "record_type": "record",
            "mode": "import",
        },
        "transformed_data": {
            "title": "Transformed Test Importer Record",
            "description": "This is a transformed test importer record.",
        },
    }


@pytest.fixture()
def task_starter(UserFixture, app, db):
    """Community owner."""
    u = UserFixture(
        email="task_starter@up.up",
        password="task_starter",
    )
    u.create(app, db)
    return u
