"""Proxies for Bulk Importer extension and services."""

from flask import current_app
from werkzeug.local import LocalProxy

current_bulk_importer = LocalProxy(
    lambda: current_app.extensions["invenio-bulk-importer"]
)

current_importer_tasks_service = LocalProxy(lambda: current_bulk_importer.tasks_service)

current_importer_tasks_file_service = LocalProxy(
    lambda: current_bulk_importer.tasks_service.files
)

current_importer_records_service = LocalProxy(
    lambda: current_bulk_importer.records_service
)
