# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module tests."""

from flask import Flask

from invenio_bulk_importer import InvenioBulkImporter


def test_version():
    """Test version import."""
    from invenio_bulk_importer import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioBulkImporter(app)
    assert "invenio-bulk-importer" in app.extensions

    app = Flask("testapp")
    ext = InvenioBulkImporter()
    assert "invenio-bulk-importer" not in app.extensions
    ext.init_app(app)
    assert "invenio-bulk-importer" in app.extensions


def test_view(base_client):
    """Test view."""
    res = base_client.get("/")
    assert res.status_code == 200
    assert "Welcome to Invenio-Bulk-Importer" in str(res.data)
