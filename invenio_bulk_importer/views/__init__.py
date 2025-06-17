# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""View blueprints for Invenio Bulk Importer."""

from .api import (
    blueprint, create_records_bp, create_tasks_bp,
)

__all__ = (
    "blueprint",
    "create_records_bp",
    "create_tasks_bp",
)
