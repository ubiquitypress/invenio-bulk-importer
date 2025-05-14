from invenio_bulk_importer.serializers.records.csv import CSVRDMRecordSerializer


def test_record_transform(running_app, csv_rdm_record):
    """."""
    serializer = CSVRDMRecordSerializer()
    result = serializer.transform(csv_rdm_record)

    # Access
    assert result
    assert result["access"] == {
        "record": "public",
        "files": "restricted",
        "embargo": {"active": "TRUE", "reason": "espionage", "until": "2120-10-06"},
    }
    # See thruthy values here https://marshmallow.readthedocs.io/en/stable/marshmallow.fields.html#marshmallow.fields.Boolean

    # Files
    # assert result["files"] == ["treatment.pdf", "image1.png"]
    # Metadata
    assert result["metadata"]
    metadata = result["metadata"]
    assert metadata["resource_type"] == {"id": "publication"}
    assert metadata["creators"] == [
        {
            "affiliations": [{"name": "Museum für Naturkunde"}],
            "person_or_org": {
                "family_name": "Schlüter",
                "given_name": "Nils",
                "identifiers": [
                    {"identifier": "0000-0002-5699-3684", "scheme": "orcid"}
                ],
                "type": "personal",
            },
        },
        {
            "affiliations": [{"name": "CERN"}],
            "person_or_org": {
                "family_name": "John",
                "given_name": "Smith",
                "type": "personal",
            },
        },
    ]
    assert metadata["title"] == "Micraster ernsti Schlüter 2024, sp. nov."
    assert metadata["publication_date"] == "2024-01-18"
    assert metadata["description"]
    assert metadata["additional_descriptions"] == [
        {"description": "abstract", "type": {"id": "abstract"}},
        {"description": "methods", "type": {"id": "method"}, "lang": {"id": "eng"}},
        {"description": "notes", "type": {"id": "notes"}},
    ]
    assert metadata["languages"] == [{"id": "eng"}]
    assert metadata["version"] == "1.0.1"
    assert metadata["publisher"] == "Ubiquity Press"
    assert metadata["subjects"] == [{"subject": "custom"}]
