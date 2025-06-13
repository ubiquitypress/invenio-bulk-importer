# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Serializer utils module."""


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


def process_grouped_fields(original: dict, prefix: str) -> list:
    """Process grouped fields in the input dictionary.

    Args:
        original (dict): The original dictionary containing grouped fields.
        prefix (str): The prefix used to identify the grouped fields.
    Returns:
        list: A list of dictionaries representing the grouped fields.
    """
    group_input = {
        key: value for key, value in original.items() if key.startswith(f"{prefix}.")
    }
    # Get a temporary list of item information for easier working.
    try:
        num_items = max(len(value.split("\n")) for value in group_input.values())
    except Exception:
        num_items = 0

    output = []
    keys = group_input.keys()
    for i in range(num_items):
        item_dict = {}
        for key in keys:
            parts = key.split(".")
            values = group_input[key].split("\n")
            item_dict[".".join(parts[1:])] = (
                values[i] if i < len(values) and values[i].strip() else None
            )
        # Remove list dict item if all values are None
        if all(value is None for value in item_dict.values()):
            continue
        output.append(item_dict)
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
