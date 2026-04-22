# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Serializer utils module."""

from typing import Any


def process_grouped_fields_via_column_title(
    original: dict, group_prefix: str, main_key: str
) -> dict:
    """Process grouped fields in the input dictionary, where column name dictates the grouping type and language.

    Column in CSV can be defined with a type and language (optional), e.g.:
    - <group_prefix>.<type>.<lang>
      - additional_descriptions.methods.eng

    this would create:

    "additional_descriptions": [
        {<main_key>: "value in column", "type": {"id": "method"}, "lang": {"id": "eng"}}
    ]

    - <group_prefix>.<type>
      - additional_titles.alternative-title

    this would create:

    "additional_descriptions": [
        {<main_key>: "value in column", "type": {"id": "alternative-title"}}
    ]

    Args:
        original (dict): The original dictionary containing grouped fields.
        group_prefix (str): The prefix used to identify the grouped fields.
        main_key (str): The main key used to identify the dict of an individual group.
    Returns:
        dict: A dictionary representing the grouped fields.
    """
    output = []
    for key, value in original.items():
        if key.startswith(f"{group_prefix}.") and value:
            _, *modifiers = key.split(".")
            info = {"type": {"id": modifiers[0]}}
            if len(modifiers) == 2:
                # We have language information, i.e. "desciption.abstract.eng"
                info["lang"] = {"id": modifiers[1]}
            output.append({main_key: value, **info})
    original[group_prefix] = output
    return original


def process_grouped_fields(
    original: dict, prefix: str, drop_empty: bool = True
) -> list[dict]:
    r"""Process grouped fields in the input dictionary.

    Columns whose names start with ``<prefix>.`` are expected to contain
    newline-separated values. Their cells are split and transposed into a
    list of per-row dictionaries, one entry per line.

    Example::

        original = {
            "rights.id":    "cc-by-4.0\\ncc-0",
            "rights.title": "CC BY 4.0\\nCC 0",
        }
        process_grouped_fields(original, "rights") == [
            {"id": "cc-by-4.0", "title": "CC BY 4.0"},
            {"id": "cc-0",      "title": "CC 0"},
        ]

    :param original: The dictionary containing grouped fields.
    :param prefix: The column-name prefix identifying the group.
    :param drop_empty: If True (default), rows where every value is ``None``
        are omitted. Set to False when positional alignment with another
        group must be preserved (e.g. pairing funders with awards).
    :return: A list of dictionaries, one per row.
    """
    pfx = f"{prefix}."
    split = {
        key[len(pfx) :]: value.split("\n")
        for key, value in original.items()
        if key.startswith(pfx)
    }
    num_items = max((len(v) for v in split.values()), default=0)

    output = []
    for i in range(num_items):
        item = {
            subkey: (parts[i].strip() if i < len(parts) and parts[i].strip() else None)
            for subkey, parts in split.items()
        }
        if drop_empty and all(v is None for v in item.values()):
            continue
        output.append(item)
    return output


def generate_error_messages(errors: list) -> list[dict]:
    """Generate error messages from a list of errors.

    Args:
        errors (list): A list of errors to process.
    Returns:
        list: List containing Error objects with type, loc, and msg attributes.
    """
    error_messages = []
    for error in errors:
        error_messages.append(
            dict(
                type=error["type"],
                loc=".".join(str(item) for item in error["loc"]),
                msg=error["msg"],
            )
        )
    return error_messages


def strip_string_values(obj: dict[str, Any]) -> dict[str, Any]:
    """Stript white spaces from string values inside a dictionary.

    :param obj: The dictionary to strip string from.
    :return: A copy of the dictionary witht he stripped values.
    """
    new_dict = {}
    for k, v in obj.items():
        if isinstance(v, str):
            new_dict[k] = v.strip()
        elif isinstance(v, dict):
            new_dict[k] = strip_string_values(v)
        elif isinstance(v, list):
            new_dict[k] = [strip_string_values(i) for i in v]
        else:
            new_dict[k] = v
    return new_dict
