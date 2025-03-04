# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CSV RDM record serializer."""

from flask import current_app
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.tasks import system_identity
from marshmallow import EXCLUDE, Schema, ValidationError, fields, post_load
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode

from invenio_bulk_importer.serializers.base import CSVSerializer


class NewlineList(fields.Field):
    """Custom Marshmallow field to handle newline-separated lists."""

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return []
        return [v.strip() for v in value.split("\n")]


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
    resource_type = fields.Method(
        "get_resource_type",
        data_key="resource_type.id",
        deserialize="load_resource_type",
        required=True,
    )
    languages = fields.Method(
        "get_language",
        data_key="languages.id",
        deserialize="load_languages",
    )

    def get_resource_type(self, obj):
        raise NotImplementedError()

    def get_language(self, obj):
        return NotImplementedError()

    def load_resource_type(self, value):
        if not value:
            raise ValidationError("Missing 'resource_type.id'", "resource_type")
        return {"id": value}

    def load_languages(self, value):
        if not value:
            return []
        return [{"id": lang} for l in value.split("\n") if (lang := l.strip())]

    def load_creatibutor(self, original, creatibutor_type):
        output = {creatibutor_type: []}
        people_input = {
            key: value
            for key, value in original.items()
            if key.startswith(f"{creatibutor_type}.")
        }
        # Determine the number of people
        num_people = max(len(value.split("\n")) for value in people_input.values())

        # Initialize a list of dictionaries for each person
        people = [{} for _ in range(num_people)]
        for key, value in people_input.items():
            parts = key.split(".")
            values = value.split("\n")

            for i in range(num_people):
                person = people[i]
                val = values[i] if i < len(values) else ""

                if not val:
                    continue
                if parts[1] in ["type", "given_name", "family_name", "name"]:
                    person[parts[1]] = val
                # TODO: allow for more than this identifier types
                elif parts[1] in ["orcid", "gnd", "isni", "ror"]:
                    if "identifiers" not in person:
                        person["identifiers"] = []
                    person["identifiers"].append(
                        {"scheme": parts[1], "identifier": val}
                    )
                elif parts[1] == "affiliations":
                    if "affiliations" not in person:
                        person["affiliations"] = []
                    affiliation = {}
                    if parts[2] == "id":
                        affiliation["id"] = val
                    elif parts[2] == "name":
                        affiliation["name"] = val
                    person["affiliations"].append(affiliation)
                elif parts[1] == "role":
                    if parts[2] == "id":
                        person["role"] = dict(id=val)

        cleaned_people = [person for person in people if person]

        # Validate and add the processed people to the output
        for person in cleaned_people:
            affiliations = person.pop("affiliations", [])
            person_type = person.get("type")
            if person_type not in ["organizational", "personal"]:
                raise ValidationError(
                    "Invalid type. Only 'organizational' and 'personal' are supported.",
                    creatibutor_type,
                )
            if person_type == "organizational" and "name" not in person:
                raise ValidationError(
                    "An organizational person must have 'name' filled in",
                    creatibutor_type,
                )
            elif person_type == "personal" and "family_name" not in person:
                raise ValidationError(
                    "A personal person must have 'family_name' filled in",
                    creatibutor_type,
                )

            output[creatibutor_type].append(
                {"person_or_org": person, "affiliations": affiliations}
            )
        return output

    def load_additional_description(self, original):
        """Load addictional desciptions."""
        output = {"additional_descriptions": []}

        for key, value in original.items():
            if key.startswith("description.") and value:
                _, *modifiers = key.split(".")
                info = {"type": {"id": modifiers[0]}}
                if len(modifiers) == 2:
                    # We have language information, i.e. "desciption.abstract.eng"
                    info["lang"] = {"id": modifiers[1]}

                output["additional_descriptions"].append({"description": value, **info})

        return output

    def load_subjects(self, original):
        output = {"subjects": []}

        keywords = original.get("keywords", "")

        for k in keywords.split("\n"):
            if keyword := k.strip():
                output["subjects"].append({"subject": keyword})

        subjects = original.get("subjects.subject", "").split("\n")
        schemes = original.get("subjects.scheme", "").split("\n")

        if len(subjects) != len(schemes):
            raise ValidationError("Each subject must have a schema and a subject")

        subjects_service = current_service_registry.get("subjects")
        for subject, scheme in zip(subjects, schemes):
            hits = subjects_service.search(
                system_identity,
                params={"q": f'subject:"{subject}" AND scheme:"{scheme}"'},
            )
            if hits.total != 1:
                # To avoid non predictable outputs we only allow for one match
                raise ValidationError(f"Subject {scheme}:{subject} cannot be matched.")

            subject = next(hits.hits)

            output["subjects"].append(
                {
                    "id": subject["id"],
                    "subject": subject["subject"],
                }
            )

        return output

    @post_load(pass_original=True)
    def load_complex_fields(self, result, original, **kwargs):
        """Remove empty values from the resulting dicionary."""
        creators = self.load_creatibutor(original, "creators")
        contributors = self.load_creatibutor(original, "contributors")
        additional_descriptions = self.load_additional_description(original)
        subjects = self.load_subjects(original)

        result.update(creators)
        result.update(contributors)
        result.update(additional_descriptions)
        result.update(subjects)

        # Filter empty values
        return {k: v for k, v in result.items() if v}


class CSVRecordSchema(Schema):
    """CSV RDM Record marchmallow schema."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    id = fields.String()
    default_community = fields.String()
    communities = NewlineList()
    files = NewlineList(data_key="filenames")

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
