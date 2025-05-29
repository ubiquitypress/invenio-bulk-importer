# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Example custom field transformer module."""

from invenio_bulk_importer.serializers.records.utils import process_grouped_fields


def imprint_transform(values) -> dict:
    """Transform imprint values into a dictionary as a custom field.

    Config in importer would be as follows:
    ```python
    app_config["BULK_IMPORTER_CUSTOM_FIELDS"] = {
        "csv_rdm_record_serializer": [
            {
                "field": "imprint:imprint",
                "transformer": "invenio_bulk_importer.serializers.records.examples.transformers.imprint_transform""
            }
        ]
    }
    ```

    Args:
        values (dict): The input dictionary containing imprint values.
    """

    def pop_or_update_key(dict_output: dict, key: str, value: str):
        """Pop or update a key in the dictionary."""
        if value:
            dict_output[key] = value
        else:
            dict_output.pop(key)

    # CSV columnname prefix
    KEY_PREFIX: str = "imprint"
    # Expected imprint columns to be prefixed with "imprint."
    COLUMN_NAMES: list = ["isbn", "pages", "edition", "place", "volume", "series_name"]
    # Get grouped fields
    temp_output = process_grouped_fields(values, KEY_PREFIX)

    dict_output = {
        "isbn": None,
        "pages": None,
        "edition": None,
        "place": None,
        "volume": None,
        "series_name": None,
    }
    for imprint in temp_output:
        for COLUMN_NAME in COLUMN_NAMES:
            pop_or_update_key(dict_output, COLUMN_NAME, imprint.get(COLUMN_NAME, None))
        # Only a single imprint is expected
        break
    # Remove list dict item if all values are None
    if all(value is None for value in dict_output.values()):
        return {}
    return dict_output
