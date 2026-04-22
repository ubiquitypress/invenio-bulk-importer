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
        self.csv_excluded_fields.extend(
            (
                "access.status",
                "resource_type.title",
                "role.title",
                "languages.title",
            )
        )

    def _preprocess_access(self, access):
        """Preprocess the access dictionary.

        Remove the status key, we don't want it in the export.
        """
        if not access.get("embargo", {}).get("active", False):
            access.pop("embargo", None)
        return access

    def _parse_groupped_fields(self, values, main_key):
        res = {}
        for d in values:
            key = f"additional_descriptions.{d['type']['id']}"
            if lang := d.get("lang"):
                key = f"{key}.{lang['id']}"
            res[key] = d[main_key]
        return res

    def _preprocess_metadata(self, metadata):
        """Preprocess the metadata dictionary.

        - Process creatibutors removing `person_or_org`.
        """

        def parse_creatibutors(creatibutors):
            res = []
            for c in creatibutors:
                person_or_org = c.get("person_or_org", {})
                flatten_creator = {**person_or_org}

                identifiers = flatten_creator.pop("identifiers", [])
                for identifier in identifiers:
                    flatten_creator[f"identifiers.{identifier['scheme']}"] = identifier[
                        "identifier"
                    ]

                if role := person_or_org.get("role"):
                    flatten_creator["role"] = {"id": role["id"]}

                if affiliations := person_or_org.get("affiliations"):
                    flatten_creator["affiliations"] = affiliations

                res.append(flatten_creator)

            return res

        metadata["creators"] = parse_creatibutors(metadata["creators"])
        if contriuborts := metadata.get("contributors"):
            metadata["contributors"] = parse_creatibutors(contriuborts)

        return metadata

    def _process_files(self, files):
        """."""
        return "\n".join(files.get("entries", {}).keys())

    def process_dict(self, dictionary):
        access = self._flatten(
            self._preprocess_access(dictionary.get("access", {})),
            parent_key="access",
        )
        metadata = dictionary.get("metadata")
        # Process special fields that are collapased into one column
        additional_descriptions = self._parse_groupped_fields(
            metadata.pop("addition_descriptions", []), "desciption"
        )
        additional_titles = self._parse_groupped_fields(
            metadata.pop("additional_titles", []), "title"
        )
        # Process the rest of the metadata
        metadata = self._flatten(self._preprocess_metadata(metadata))

        files = self._process_files(dictionary.get("files", {}))

        custom_fields = self._flatten(dictionary.get("custom_fields", {}))

        return {
            "id": dictionary["id"],
            "files": files,
            **access,
            **metadata,
            **additional_descriptions,
            **additional_titles,
            **custom_fields,
        }
