# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Importer task service components."""
from invenio_records_resources.services.records.components import ServiceComponent


class ImporterTaskServiceComponent(ServiceComponent):
    """Importer Task Service Component."""

    # store user identity only on create, ignore later
    def create(self, identity, *, record, **kwargs):
        """Create a new importer task."""
        record.update_start_by_id(identity.user.id)


class ImporterRecordServiceComponent(ServiceComponent):
    """Importer Task Service Component."""

    # store user identity only on create, ignore later
    def create(self, identity, *, record, task_id, **kwargs):
        """Create a new importer task."""
        record.update_task_id(task_id)
