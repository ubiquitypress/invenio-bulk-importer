# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Importer Task Service Schema."""
import marshmallow as ma
from invenio_i18n import gettext as _
from invenio_records_resources.services.records.schema import (
    BaseRecordSchema as InvenioBaseRecordSchema,
)
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode


class FilesSchema(ma.Schema):
    """Basic files schema class."""

    enabled = ma.fields.Bool(missing=True)
    # allow unsetting
    default_preview = SanitizedUnicode(allow_none=True)

    def get_attribute(self, obj, attr, default):
        """Override how attributes are retrieved when dumping.

        NOTE: We have to access by attribute because although we are loading
              from an external pure dict, but we are dumping from a data-layer
              object whose fields should be accessed by attributes and not
              keys. Access by key runs into FilesManager key access protection
              and raises.
        """
        value = getattr(obj, attr, default)

        if attr == "default_preview" and not value:
            return default

        return value


def validate_mode(value):
    """Check if the value is a valid mode setting."""
    if value not in ["import", "delete"]:
        raise ma.ValidationError(
            message=str(_("Value must be either 'import' or 'delete'."))
        )


def validate_record_status(value):
    """Check if the value is a valid status setting."""
    if value not in [
        "created",
        "creation failed",
        "validating",
        "serializer validation failed",
        "validation failed",
        "validated",
        "success",
        "stopped",
    ]:
        raise ma.ValidationError(
            message=str(
                _(
                    f"Value '{value}' must be one of: 'created', 'validating', 'running', 'success', 'failure', 'stopped', 'archived', or 'warnings'."
                )
            )
        )


def validate_task_status(value):
    """Check if the value is a valid status setting."""
    if value not in [
        "created",
        "validating",
        "running",
        "success",
        "failure",
        "stopped",
        "archived",
        "warnings",
    ]:
        raise ma.ValidationError(
            message=str(
                _(
                    "Value must be one of: 'created', 'validating', 'running', 'success', 'failure', 'stopped', 'archived', or 'warnings'."
                )
            )
        )


class UserSchema(ma.Schema):
    """User schema for the started_by field."""

    id = ma.fields.Integer(dump_only=True)
    username = ma.fields.String(dump_only=True)
    email = ma.fields.Email(dump_only=True)

    class Meta:
        """Meta class for User Schema."""

        unknown = ma.RAISE


class ImporterTaskSchema(InvenioBaseRecordSchema):
    """Importer Task Service Schema."""

    class Meta:
        """Meta class for Importer Task Schema."""

        unknown = ma.RAISE

    title = ma.fields.String(
        required=True,
        validate=ma.validate.Length(min=1, max=255),
    )
    description = ma.fields.String(
        allow_none=True,
        validate=ma.validate.Length(max=1000),
    )
    mode = ma.fields.String(validate=validate_mode, required=True)
    record_type = ma.fields.String(
        required=True,
        validate=ma.validate.Length(min=1, max=255),
    )
    serializer = ma.fields.String(
        required=True,
        validate=ma.validate.Length(min=1, max=255),
    )
    start_time = ma.fields.DateTime(allow_none=True)
    end_time = ma.fields.DateTime(allow_none=True)
    records_status = ma.fields.Dict(allow_none=True)
    status = ma.fields.String(validate=validate_task_status, required=True)
    files = NestedAttribute(FilesSchema)
    started_by = ma.fields.Nested(UserSchema, dump_only=True)


class RelatedImporterTaskSchema(ma.Schema):
    """Related Importer Task Schema for Importer Record."""

    id = ma.fields.String(dump_only=True)


class ImportErrorSchema(ma.Schema):
    """Schema for Importer Record errors."""

    msg = ma.fields.String(
        required=True,
        description="Error message describing the issue encountered during import.",
    )
    loc = ma.fields.String(
        required=True,
        description="Location of the error.",
    )
    type = ma.fields.String(
        required=True,
        description="Type of error encountered during import (e.g., 'validation', 'processing').",
    )


class ImporterRecordSchema(InvenioBaseRecordSchema):
    """Importer Record Service Schema."""

    class Meta:
        """Meta class for Importer Record Schema."""

        unknown = ma.RAISE

    status = ma.fields.String(validate=validate_record_status, required=True)
    message = ma.fields.String(
        allow_none=True,
        validate=ma.validate.Length(max=1000),
    )
    src_data = ma.fields.Dict(
        allow_none=True,
        description="Source data dictionary before being validated by serializer.",
    )
    serializer_data = ma.fields.Dict(
        allow_none=True,
        description="Serialized data of a record, if applicable.",
    )
    transformed_data = ma.fields.Dict(
        allow_none=True,
        description="Transformed data of a record, if applicable.",
    )
    community_uuids = ma.fields.Dict(
        allow_none=True,
        description="Community uuids to link to the record.",
    )
    record_files = ma.fields.List(
        ma.fields.String(),
        allow_none=True,
        description="List of file name, urls and cloud bucket urls to be associated with the record.",
    )
    validated_record_files = ma.fields.List(
        ma.fields.Dict(),
        allow_none=True,
        description="List of validated files with key, size and origin.",
    )
    generated_record_id = ma.fields.String(
        allow_none=True,
        description="Generated record ID after successful import.",
    )
    errors = ma.fields.List(
        ma.fields.Nested(ImportErrorSchema),
    )
    task = ma.fields.Nested(RelatedImporterTaskSchema, dump_only=True)
