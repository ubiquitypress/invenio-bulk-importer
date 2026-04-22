# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Importer task links."""

from invenio_records_resources.services import EndpointLink


class ImporterLink(EndpointLink):
    """Short cut for writing record links."""

    @staticmethod
    def vars(obj, vars):
        """Variables for the URI template."""
        pid_value = getattr(obj, "pid", None)
        if pid_value:
            vars.update({"id": obj.id})
