from invenio_bulk_importer.serializers.records.csv import CSVRDMRecordSerializer


def test_record_transform(appctx, csv_rdm_record):
    """."""
    serializer = CSVRDMRecordSerializer()
    result = serializer.transform(csv_rdm_record)

    assert result
    assert result["access"] == {"record": "public", "files": "public"}
