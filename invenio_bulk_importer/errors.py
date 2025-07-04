# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Exception for Invenio Bulk Importer."""


class ImporterTaskNoReadyError(Exception):
    """Exception raised when the importer task is not in the expected status."""
