# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration importer task module."""

from functools import partial

from flask import current_app
from invenio_administration.views.base import AdminResourceListView
from invenio_search_ui.searchconfig import search_app_config


class ImporterTaskListView(AdminResourceListView):
    """Search admin view."""

    api_endpoint = "/importer-tasks"
    extension_name = "invenio-bulk-importer"
    name = "importer-tasks"
    resource_config = "tasks_resource"
    search_request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}
    title = "Bulk importer"
    menu_label = "Importer Tasks"
    category = "Bulk Importer"
    pid_path = "id"
    icon = "copy"
    template = "invenio_bulk_importer/administration/importer_tasks_search.html"

    display_search = True
    display_delete = False
    display_create = False
    display_edit = False

    search_config_name = "BULK_IMPORTER_TASKS_SEARCH"
    search_facets_config_name = "BULK_IMPORTER_TASKS_FACETS"
    search_sort_config_name = "BULK_IMPORTER_TASKS_SORT_OPTIONS"

    def init_search_config(self):
        """Build search view config."""
        return partial(
            search_app_config,
            config_name=self.get_search_app_name(),
            available_facets=current_app.config.get(self.search_facets_config_name),
            sort_options=current_app.config[self.search_sort_config_name],
            endpoint=self.get_api_endpoint(),
            headers=self.get_search_request_headers(),
            pagination_options=(20, 50),
            default_size=20,
        )
