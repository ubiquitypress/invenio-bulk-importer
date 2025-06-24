# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Parser for request body in Invenio Bulk Importer."""

from flask import request


class RequestFileNameAndStreamParser:
    """Parse the request body."""

    def parse(self):
        """Parse the request body."""
        return {
            "request_filename": request.headers.get("X-Filename"),
            "request_stream": request.stream,
            "request_content_length": request.content_length,
        }
