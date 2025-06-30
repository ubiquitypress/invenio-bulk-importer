# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources for importer tasks and records."""

from .config import (
    ImporterRecordResourceConfig,
    ImporterTaskFilesResourceConfig,
    ImporterTaskResourceConfig,
)
from .resources import ImporterRecordResource, ImporterTaskResource

__all__ = (
    "ImporterRecordResource",
    "ImporterRecordResourceConfig",
    "ImporterTaskFilesResourceConfig",
    "ImporterTaskResource",
    "ImporterTaskResourceConfig",
)
