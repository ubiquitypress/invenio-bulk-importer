# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Fixtures for Invenio Bulk Importer tests."""

import pytest
from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session


@pytest.fixture()
def headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/json",
    }


@pytest.fixture()
def admin_client(client, user_admin, app, db):
    """Log in a user to the client."""
    user = user_admin.user
    # login_user(user)
    login_user_via_session(client, email=user.email)
    return client
