"""Test InvenioRDM record serializers to export CSV."""

import csv
import io

from invenio_bulk_importer.contrib.rdm_record_serializer import CSVSerializer


def test_basic_csv_serializer(minimal_record_to_dict):
    """Basic bulk importer csv ecport."""
    serializer = CSVSerializer()

    serialized_data = serializer.serialize_object(minimal_record_to_dict)
    # Read the serialized data using the CSV module for convenience
    # I also tests for correct output format ;-)
    stream = io.StringIO(serialized_data)
    data = next(csv.DictReader(stream))
    expected_keys = {
        "id",
        "access.files",
        "access.record",
        "resource_type.id",
        "title",
        "publisher",
        "publication_date",
        "creators.family_name",
        "creators.given_name",
        "creators.name",
        "creators.type",
    }
    assert data.keys() == expected_keys


def test_full_record_csv_serializer(full_record_dict):
    """Full record bulk importer csv ecport."""
    serializer = CSVSerializer()

    serialized_data = serializer.serialize_object(full_record_dict)
    # Read the serialized data using the CSV module for convenience
    # I also tests for correct output format ;-)
    stream = io.StringIO(serialized_data)
    data = next(csv.DictReader(stream))
    expected_keys = {
        "id",
        "access.files",
        "access.record",
        "access.embargo.active",
        "access.embargo.reason",
        "access.embargo.until",
        "resource_type.id",
        "title",
        "publisher",
        "publication_date",
        "creators.family_name",
        "creators.given_name",
        "creators.name",
        "creators.type",
    }
    assert data.keys() == expected_keys
