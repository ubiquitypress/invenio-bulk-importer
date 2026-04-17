# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Paradigm Repositories.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""CSV serializer compatible with the bulk importer.

To use it, update the current serializers from
`invenio_rdm_records.resources.config.record_serializers` adding an instance of
`CSVSerializer` properly configured to your needs. The content type can be something like
`application/vnd.inveniordm.v1.bulk+csv`.

Here is an example:
TODO
"""

from invenio_rdm_records.resources.serializers.csv import (
    CSVSerializer as _CSVSerializer,
)


class CSVSerializer(_CSVSerializer):
    """CSV serializer compatible with the bulk importer.

    It differs from the RDM one just in how it treats list fields. In this case it always
    collapeses a set of fields into one column using newlines to separate values.
    It also simplifies the path on some instances like `metadata.creators.person_or_org.type`
    is replaced by `creators.type`

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collapse_lists = True
        self.header_separator = "."
        self.csv_excluded_fields.extend(("access.status", "resource_type.title"))

    def _preprocess_access(self, access):
        """Preprocess the access dictionary.

        Remove the status key, we don't want it in the export.
        """
        if not access.get("embargo", {}).get("active", False):
            access.pop("embargo")
        return access

    def _preprocess_metadata(self, metadata):
        """Preprocess the metadata dictionary.

        - Process creatibutors removing `person_or_org`.
        """
        creators = []
        for c in metadata["creators"]:
            creators.append(c["person_or_org"])
        metadata["creators"] = creators

        return metadata

    def process_dict(self, dictionary):
        access = self._flatten(
            self._preprocess_access(dictionary.get("access", {})),
            parent_key="access",
        )
        metadata = self._flatten(
            self._preprocess_metadata(dictionary.get("metadata", {}))
        )
        custom_fields = self._flatten(dictionary.get("custom_fields", {}))
        return {"id": dictionary["id"], **access, **metadata, **custom_fields}
