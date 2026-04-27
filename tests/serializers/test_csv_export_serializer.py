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
        "creators.identifiers.orcid",
        "creators.name",
        "creators.type",
        "dates.date",
        "dates.description",
        "dates.type.id",
        "description",
        "files",
        "formats",
        "funding.award.id",
        "funding.award.number",
        "funding.award.title",
        "funding.funder.id",
        "funding.funder.name",
        "id",
        "identifiers.identifier",
        "identifiers.scheme",
        "keywords",
        "languages.id",
        "locations.description",
        "locations.lat",
        "locations.lon",
        "locations.place",
        "publication_date",
        "publisher",
        "references.identifier",
        "references.reference",
        "references.scheme",
        "related_identifiers.identifier",
        "related_identifiers.relation_type.id",
        "related_identifiers.resource_type.id",
        "related_identifiers.scheme",
        "resource_type.id",
        "rights.id",
        "rights.link",
        "rights.title",
        "rights.description",
        "sizes",
        "subjects.scheme",
        "subjects.subject",
        "title",
        "version",
    }
    assert set(data.keys()) == expected_keys
