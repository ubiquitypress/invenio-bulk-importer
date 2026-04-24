"""Test InvenioRDM record serializers to export CSV."""

import csv
import io

from invenio_bulk_importer.serializers.records.csv_export import CSVSerializer


def test_record_csv_serializer(full_record_dict):
    """Full record bulk importer csv ecport."""
    serializer = CSVSerializer()

    serialized_data = serializer.serialize_object(full_record_dict)
    # Read the serialized data using the CSV module for convenience
    # I also tests for correct output format ;-)
    stream = io.StringIO(serialized_data)
    data = next(csv.DictReader(stream))
    expected_keys = {
        "access.embargo.active",
        "access.embargo.reason",
        "access.embargo.until",
        "access.files",
        "access.record",
        "additional_descriptions.methods.eng",
        "additional_titles.subtitle.eng",
        "contributors.family_name",
        "contributors.given_name",
        "contributors.identifiers.orcid",
        "contributors.name",
        "contributors.type",
        "creators.family_name",
        "creators.given_name",
        "creators.name",
        "creators.type",
        "dates.date",
        "dates.description",
        "dates.type.id",
        "description",
        "files",
        "formats",
        "award.number",
        "funder.id",
        "funder.name",
        "languages.id",
        "publication_date",
        "publisher",
        "resource_type.id",
        "sizes",
        "title",
        "version",
    }
    assert data.keys() == expected_keys
