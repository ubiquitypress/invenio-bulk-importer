# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""General fixtures."""

import pytest
from invenio_app.factory import create_api


@pytest.fixture(scope="module")
def create_app():
    """Create app."""
    return create_api
