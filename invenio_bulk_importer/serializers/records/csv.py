# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CSV RDM record serializer."""

from flask import current_app
from marshmallow import EXCLUDE, Schema, fields, post_load
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode

from invenio_bulk_importer.serializers.base import CSVSerializer


class NewlineList(fields.Field):
    """Custom Marshmallow field to handle newline-separated lists."""

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return []
        return value.split("\n")


class MetadataSchema(Schema):
    """Schema for handling etadata fields."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    title = fields.String()
    publication_date = fields.String()
    description = fields.String()
    version = fields.String()
    publisher = fields.String()

    @post_load
    def filter_values(self, value, **kwargs):
        """Remove empty values from the resulting dicionary."""
        return {k: v for k, v in value.items() if v is not None}


class AccessSchema(Schema):
    """Access schema."""

    record = SanitizedUnicode(data_key="access.record", load_default="public")
    files = SanitizedUnicode(data_key="access.files", load_default="public")


class CSVRecordSchema(Schema):
    """CSV RDM Record marchmallow schema."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    id = fields.String()
    default_community = fields.String()
    communities = NewlineList()
    files = NewlineList(data_key="filenames")
    access = NestedAttribute(AccessSchema)

    def load_access(self, original):
        """Load the access fields."""
        access = dict(
            record=original.get("access.record", None) or "public",
            files=original.get("access.files", None) or "public",
        )

        # Extract access fields
        embargo_active = original.get("access.embargo.active", None)
        embargo_until = original.get("access.embargo.until", None)
        embargo_reason = original.get("access.embargo.reason", None)

        if embargo_active or embargo_until or embargo_reason:
            access["embargo"] = {
                "active": embargo_active,
                "until": embargo_until,
                "reason": embargo_reason,
            }

        return access

    def load_custom_fields(self, original):
        """Load custom fields from config."""
        custom_fields = dict()
        config = current_app.config.get("IMPORTER_CUSTOM_FIELDS", {}).get(
            "csv_rdm_record_serializer", []
        )
        for t in config:
            custom_fields[t["field"]] = t["transfromer"](original)

        return custom_fields

    @post_load(pass_original=True)
    def load_complex_metadata(self, result, original, **kwargs):
        """Load all complex metadata after initial load."""
        access = self.load_access(original)
        custom_fields = self.load_custom_fields(original)
        metadata = MetadataSchema().load(original)

        result.update(
            {"access": access, "custom_fields": custom_fields, "metadata": metadata}
        )
        return result


class CSVRDMRecordSerializer(CSVSerializer):
    """Serializer for RDM records."""

    def transform(self, obj: dict) -> dict:
        """."""
        schema = CSVRecordSchema()
        return schema.load(obj)
