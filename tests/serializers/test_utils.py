# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Unit tests for serializer utilities."""

from invenio_bulk_importer.serializers.records.utils import process_grouped_fields


def test_basic_transpose():
    """Newline-separated cells are split into a list of per-row dicts."""
    original = {
        "rights.id": "cc-by-4.0\ncc-0",
        "rights.title": "CC BY 4.0\nCC 0",
    }
    assert process_grouped_fields(original, "rights") == [
        {"id": "cc-by-4.0", "title": "CC BY 4.0"},
        {"id": "cc-0", "title": "CC 0"},
    ]


def test_prefix_isolation():
    """Keys without the prefix must be ignored, prefix match must be exact."""
    original = {
        "rights.id": "cc-by-4.0",
        "rightsholder.id": "should not leak",
        "other": "ignored",
    }
    assert process_grouped_fields(original, "rights") == [{"id": "cc-by-4.0"}]


def test_empty_input():
    """No matching keys returns an empty list (no exception)."""
    assert process_grouped_fields({}, "anything") == []
    assert process_grouped_fields({"foo": "bar"}, "rights") == []


def test_non_string_values_are_skipped():
    """Non-string values (e.g. already-parsed fields) are ignored, not crashed on."""
    original = {
        "rights.id": "cc-0",
        "rights.parsed": ["already", "a", "list"],
    }
    assert process_grouped_fields(original, "rights") == [{"id": "cc-0"}]


def test_whitespace_is_stripped():
    """Values are stripped consistently."""
    original = {"rights.id": "  cc-0  \n  cc-by-4.0  "}
    assert process_grouped_fields(original, "rights") == [
        {"id": "cc-0"},
        {"id": "cc-by-4.0"},
    ]


def test_ragged_columns_pad_with_none():
    """When columns have unequal line counts, shorter columns pad with None."""
    original = {
        "rights.id": "cc-0\ncc-by-4.0\ncc-by-sa",
        "rights.title": "CC 0\nCC BY 4.0",
    }
    assert process_grouped_fields(original, "rights") == [
        {"id": "cc-0", "title": "CC 0"},
        {"id": "cc-by-4.0", "title": "CC BY 4.0"},
        {"id": "cc-by-sa", "title": None},
    ]


def test_drop_empty_true_drops_all_none_rows():
    """Default drop_empty=True removes rows whose values are all None."""
    original = {
        "rights.id": "cc-0\n\ncc-by-4.0",
        "rights.title": "CC 0\n\nCC BY 4.0",
    }
    assert process_grouped_fields(original, "rights") == [
        {"id": "cc-0", "title": "CC 0"},
        {"id": "cc-by-4.0", "title": "CC BY 4.0"},
    ]


def test_drop_empty_false_preserves_all_none_rows():
    """drop_empty=False keeps all-None rows so positional alignment is intact."""
    original = {
        "rights.id": "cc-0\n\ncc-by-4.0",
        "rights.title": "CC 0\n\nCC BY 4.0",
    }
    assert process_grouped_fields(original, "rights", drop_empty=False) == [
        {"id": "cc-0", "title": "CC 0"},
        {"id": None, "title": None},
        {"id": "cc-by-4.0", "title": "CC BY 4.0"},
    ]


def test_funders_and_awards_stay_aligned():
    """Regression: two paired groups must keep row indices in sync.

    When funder at index 0 has no award and funder at index 1 does, the
    ``drop_empty=False`` flag ensures ``awards[0]`` is an all-None placeholder
    rather than being dropped (which would shift ``awards[1]`` into position 0
    and pair the award with the wrong funder).
    """
    original = {
        "funders.id": "funder1\nfunder2",
        "funders.name": "Name 1\nName 2",
        "awards.id": "\naward2",
        "awards.number": "\nN-002",
    }
    funders = process_grouped_fields(original, "funders", drop_empty=False)
    awards = process_grouped_fields(original, "awards", drop_empty=False)

    assert len(funders) == len(awards) == 2
    assert funders[0] == {"id": "funder1", "name": "Name 1"}
    assert funders[1] == {"id": "funder2", "name": "Name 2"}
    # Placeholder for the first funder — no award data.
    assert awards[0] == {"id": None, "number": None}
    assert awards[1] == {"id": "award2", "number": "N-002"}


def test_nested_subkeys_preserved():
    """Subkeys after the first dot (e.g. ``identifiers.orcid``) survive intact."""
    original = {
        "creators.name": "Alice\nBob",
        "creators.identifiers.orcid": "0000-0001\n0000-0002",
    }
    assert process_grouped_fields(original, "creators") == [
        {"name": "Alice", "identifiers.orcid": "0000-0001"},
        {"name": "Bob", "identifiers.orcid": "0000-0002"},
    ]
