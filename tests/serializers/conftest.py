# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Serializer fixtures."""

import csv
from pathlib import Path

import pytest


@pytest.fixture()
def csv_rdm_record():
    """CSV RDM Record."""
    path = Path(__file__).parent / "data/rdm_records.csv"
    with path.open() as f:
        yield from csv.DictReader(f, delimiter=",", quotechar='"')
