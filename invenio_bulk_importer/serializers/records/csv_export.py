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
                "rights.props",
            )
        )

    def is_field_included(self, key):
        """Determines if a key should be included or not."""
        if key in self.csv_excluded_fields or self.field_in_key(
            key, self.csv_excluded_fields
        ):
            return False
        if self.csv_included_fields and not self.key_in_field(
            key, self.csv_included_fields
        ):
            return False
        return True

    def field_in_key(self, key, fields):
        """Checks if a field from the list is included in the key."""
        return any(field in key for field in fields)

    def _preprocess_access(self, access):
        """Preprocess the access dictionary.

        Remove the status key, we don't want it in the export.
        """
        if not access.get("embargo", {}).get("active", False):
            # If embargo is not active there is no point in having it there
            access.pop("embargo", None)
        return access

    def _parse_groupped_fields(self, values, main_key, value_key):
        res = {}
        for d in values:
            key = f"{main_key}.{d['type']['id']}"
            if lang := d.get("lang"):
                key = f"{key}.{lang['id']}"
            res[key] = d[value_key]
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

        def parse_loactions(features):
            res = []
            for f in features:
                if geometry := f.pop("geometry", None):
                    if geometry["type"] != "Point":
                        # TODO:: show we raise something or at least log a warning?
                        continue
                    f["lat"], f["lon"] = geometry["coordinates"]
                f.pop("identifiers")  # FIXME: find a way to work around these
                res.append(f)
            return res

        def parse_subjects(values):
            """Parse the subjects field to turn it into subjects (vocab) and keywords (free)."""
            res = {"keywords": [], "subjects": []}
            for value in values:
                if value.pop("id", None):  # This is vocabulary subject
                    res["subjects"].append(value)
                else:
                    res["keywords"].append(value["subject"])
            return res

        metadata["creators"] = parse_creatibutors(metadata["creators"])
        if contriuborts := metadata.get("contributors"):
            metadata["contributors"] = parse_creatibutors(contriuborts)

        if features := metadata.pop("locations", {}).get("features"):
            metadata["locations"] = parse_loactions(features)

        if subjects := metadata.pop("subjects", []):
            metadata.update(parse_subjects(subjects))

        # Flatten funding.award.title, rights.decription|title
        # This is an i18n string, but it is always set to 'en'
        for f in metadata.get("funding", []):
            if award_title := f.get("award", {}).get("title", {}).get("en"):
                f["award"]["title"] = award_title

        for r in metadata.get("rights", []):
            if title := r.get("title", {}).get("en"):
                r["title"] = title
            if desc := r.get("description", {}).get("en"):
                r["description"] = desc

        return metadata

    def _process_files(self, files):
        """Return the list of file names separated by a line break."""
        return "\n".join(files.get("entries", {}).keys())

    def process_dict(self, dictionary):
        access = self._flatten(
            self._preprocess_access(dictionary.get("access", {})),
            parent_key="access",
        )
        metadata = dictionary.get("metadata")
        # Process special fields that are collapased into one column
        additional_descriptions = self._parse_groupped_fields(
            metadata.pop("additional_descriptions", []),
            "additional_descriptions",
            "description",
        )
        additional_titles = self._parse_groupped_fields(
            metadata.pop("additional_titles", []), "additional_titles", "title"
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
