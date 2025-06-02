# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""CSV serializer for RDM records."""

from typing import Annotated, Literal

from flask import current_app
from invenio_base.utils import obj_or_import_string
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.tasks import system_identity
from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

from invenio_bulk_importer.errors import Error
from invenio_bulk_importer.serializers.base import CSVSerializer
from invenio_bulk_importer.serializers.records.utils import (
    generate_error_messages,
    process_grouped_fields,
    process_grouped_fields_via_column_title,
)


def ensure_new_line_list(value: str) -> list:
    """Ensure CSV column is converted into a list."""
    if value is None:
        return []
    return [v.strip() for v in value.split("\n")]


# Custom field to handle newline-separated lists
NewlineList = Annotated[
    list[str], BeforeValidator(ensure_new_line_list), Field(default_factory=list)
]


class Geometry(BaseModel):
    """Schema for geometry location."""

    type: str
    coordinates: list[str]


class LocationFeature(BaseModel):
    """Schema for location feature."""

    description: str
    geometry: Geometry
    place: str


class Location(BaseModel):
    """Schema for locations."""

    features: list[LocationFeature] = Field(default_factory=list)


class BaseIdentifier(BaseModel):
    """Schema for identifiers."""

    scheme: str | None = Field(default=None)
    identifier: str | None = Field(default=None)


class FullIdentifier(BaseIdentifier):
    """Schema for full identifiers."""

    resource_type: dict[str, str | None] = Field(default=None)
    relation_type: dict[str, str | None] = Field(default_factory=dict)


class Affiliation(BaseModel):
    """Schema for affiliation."""

    id: str | None = Field(default=None)
    name: str | None = Field(default=None)


class PersonOrOrg(BaseModel):
    """Schema for person or organization."""

    family_name: str | None = Field(default=None)
    given_name: str | None = Field(default=None)
    name: str | None = None
    type: Literal["personal", "organizational"]
    identifiers: list[BaseIdentifier] = Field(default_factory=list)


CreatibutorList = Annotated[
    list[dict[str, PersonOrOrg | list[Affiliation] | dict[str, str]]],
    Field(default_factory=list),
]


class MetadataSchema(BaseModel):
    """Schema for handling metadata fields."""

    title: str = Field(min_length=1)
    additional_titles: list[dict[str, str | dict[str, str]]] = Field(
        default_factory=list
    )
    publication_date: str = Field(min_length=1)
    description: str | None
    additional_descriptions: list[dict[str, str | dict[str, str]]] = Field(
        default_factory=list
    )
    version: str | None
    publisher: str
    resource_type: dict[str, str] = Field(
        default_factory=dict, alias="resource_type.id"
    )
    languages: list[dict[str, str]] = Field(default_factory=list, alias="languages.id")
    locations: Location | dict = Field(default_factory=dict)
    creators: CreatibutorList
    contributors: CreatibutorList
    subjects: list[dict[str, str]] = Field(default_factory=list)
    references: list[dict[str, str]] = Field(
        default_factory=list, alias="references.reference"
    )
    identifiers: list[BaseIdentifier] = Field(default_factory=list)
    related_identifiers: list[FullIdentifier] = Field(default_factory=list)
    rights: list[dict[str, str | dict[str, str]]] = Field(default_factory=list)

    @field_validator("resource_type", mode="before")
    def validate_resource_type(cls, value):
        """Validate resource type."""
        if not value:
            raise ValueError("Missing 'resource_type.id'")
        return {"id": value}

    @field_validator("languages", mode="before")
    def validate_languages(cls, value):
        """Validate languages."""
        if not value:
            return []
        return [{"id": lang.strip()} for lang in value.split("\n") if lang.strip()]

    @field_validator("references", mode="before")
    def validate_references(cls, value):
        """Validate references."""
        if not value:
            return []
        return [
            {"reference": reference.strip()}
            for reference in value.split("\n")
            if reference.strip()
        ]

    @model_validator(mode="before")
    def load_rights(cls, values):
        """Load rights."""
        temp_out = process_grouped_fields(values, "rights")
        output = []
        for identifier in temp_out:
            ident_dict = {}
            if identifier.get("id"):
                ident_dict["id"] = identifier.get("id")
            elif identifier.get("title"):
                ident_dict["title"] = {"en": identifier.get("title")}
            output.append(ident_dict)
        values["rights"] = output
        return values

    @model_validator(mode="before")
    def load_locations(cls, values):
        """Load locations."""
        temp_out = process_grouped_fields(values, "locations")
        output = {}
        for location in temp_out:
            if "features" not in output:
                output["features"] = []
            output["features"].append(
                {
                    "description": location.get("description"),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [location.get("lat"), location.get("lon")],
                    },
                    "place": location.get("place"),
                }
            )
        values["locations"] = output
        return values

    @model_validator(mode="before")
    def load_identifiers(cls, values):
        """Load identifiers."""
        temp_out = process_grouped_fields(values, "identifiers")
        output = []
        for identifier in temp_out:
            output.append(
                {
                    "identifier": identifier.get("identifier"),
                    "scheme": identifier.get("scheme"),
                }
            )
        values["identifiers"] = output
        return values

    @model_validator(mode="before")
    def load_related_identifiers(cls, values):
        """Load identifiers."""
        temp_out = process_grouped_fields(values, "related_identifiers")
        output = []
        for identifier in temp_out:
            new_identifier = {
                "identifier": identifier.get("identifier"),
                "scheme": identifier.get("scheme"),
                "relation_type": {
                    "id": identifier.get("relation_type.id"),
                },
                "resource_type": {
                    "id": identifier.get("resource_type.id"),
                },
            }
            if identifier.get("resource_type.id"):
                new_identifier["relation_type"] = {
                    "id": identifier.get("relation_type.id"),
                }
            output.append(new_identifier)
        values["related_identifiers"] = output
        return values

    @model_validator(mode="before")
    def load_additional_descriptions(cls, values):
        """Load addictional desciptions."""
        return process_grouped_fields_via_column_title(
            values, "additional_descriptions", "description"
        )

    @model_validator(mode="before")
    def load_additional_titles(cls, values):
        """Load addictional titles."""
        return process_grouped_fields_via_column_title(
            values, "additional_titles", "title"
        )

    @model_validator(mode="before")
    def validate_subjects(cls, values):
        """Load and transform subjects."""
        output = []

        keywords = values.get("keywords", "")

        for k in keywords.split("\n"):
            if keyword := k.strip():
                output.append({"subject": keyword})

        subjects = values.get("subjects.subject", "").split("\n")
        schemes = values.get("subjects.scheme", "").split("\n")

        if len(subjects) != len(schemes):
            raise ValueError("Each subject must have a schema and a subject")

        subjects_service = current_service_registry.get("subjects")
        for subject, scheme in zip(subjects, schemes):
            hits = subjects_service.search(
                system_identity,
                params={"q": f'subject:"{subject}" AND scheme:"{scheme}"'},
            )
            if hits.total != 1:
                # To avoid non predictable outputs we only allow for one match
                raise ValueError(f"Subject {scheme}:{subject} cannot be matched.")

            subject = next(hits.hits)

            output.append(
                {
                    "id": subject["id"],
                    "subject": subject["subject"],
                }
            )
        values["subjects"] = output
        return values

    @model_validator(mode="before")
    def validate_creators_and_contributors(cls, values):
        """Validate and transform creators and contributors."""

        def load_creatibutor(original, creatibutor_type):
            """Load and transform creators or contributors."""
            temp_output = process_grouped_fields(original, creatibutor_type)
            # Construct expected structures
            output = []
            for person in temp_output:
                # Construct person_or_org
                person_or_org = {
                    "type": person.get("type"),
                    "family_name": person.get("family_name"),
                    "given_name": person.get("given_name"),
                    "name": person.get("name"),
                }
                person_or_org["identifiers"] = []
                # Extract all keys that start with 'identifiers.'
                identifier_keys = [
                    key for key in person.keys() if key.startswith("identifiers.")
                ]
                for key in identifier_keys:
                    scheme = key.split(".")[1]  # Extract the scheme from the key
                    if val := person.get(key):
                        person_or_org["identifiers"].append(
                            {"scheme": scheme, "identifier": val}
                        )
                # Construct affiliations
                affiliations = []
                aff_names = (
                    person.get("affiliations.name", "").split(";")
                    if person.get("affiliations.name")
                    else []
                )
                aff_ids = (
                    person.get("affiliations.id", "").split(";")
                    if person.get("affiliations.id")
                    else []
                )
                max_affiliations = max(len(aff_names), len(aff_ids))
                for i in range(max_affiliations):
                    affiliation = {}
                    if i < len(aff_ids) and aff_ids[i].strip():
                        affiliation["id"] = aff_ids[i].strip()
                    if i < len(aff_names) and aff_names[i].strip():
                        affiliation["name"] = aff_names[i].strip()
                    if affiliation:
                        affiliations.append(affiliation)
                # Construct creator/contributor dict
                creatibutor_dict = {
                    "person_or_org": person_or_org,
                    "affiliations": affiliations,
                }
                # Add role if exists
                if person.get("role.id"):
                    creatibutor_dict["role"] = dict(id=person.get("role.id"))
                output.append(creatibutor_dict)
            return output

        values["creators"] = load_creatibutor(values, "creators")
        values["contributors"] = load_creatibutor(values, "contributors")
        return values

    @model_validator(mode="wrap")
    def additional_validation(cls, values, handler):
        """Wrap the validation process to add additional checks."""
        errors = []
        result = None
        # Run the default validation first
        if not isinstance(values, dict):
            # second tie around wrap after all before and after validations
            return handler(values)

        try:
            result = handler(values)
        except ValidationError as e:
            # Collect existing validation errors
            errors.extend(e.errors())
        # Add custom validation logic
        creators = values.get("creators") if errors else result.creators
        if not creators:
            creators_missing_error = PydanticCustomError(
                "no_creators_error", "Need at least one creator to be present.", {}
            )
            errors.append(
                {
                    "loc": (
                        "creators.type",
                        "creators.given_name",
                        "creators.family_name",
                        "creators.name",
                        "creators.identifiers.*",
                        "creators.affiliations.*",
                    ),
                    "type": creators_missing_error,
                    "msg": "Need at least one creator to be present.",
                }
            )

        # If there are any errors, raise a new ValidationError
        if errors:
            formatted_errors = []
            for e in errors:
                formatted_errors.append(
                    {
                        "loc": e["loc"],
                        "msg": e["msg"],
                        "type": e["type"],
                        "ctx": e.get("ctx", {}),
                    }
                )
            raise ValidationError.from_exception_data(cls.__name__, formatted_errors)

        return result


class CSVRecordSchema(BaseModel):
    """CSV RDM Record Pydantic schema."""

    id: str = Field(default=None)
    pids: dict = Field(default_factory=dict, alias="doi")
    default_community: str = Field(default=None)
    communities: NewlineList
    files: NewlineList = Field(alias="filenames")
    access: dict[str, str | dict[str, str | None]]
    custom_fields: dict[str, str | dict | list] = Field(default_factory=dict)
    metadata: MetadataSchema

    @field_validator("pids", mode="before")
    def validate_references(cls, value):
        """Validate pids."""
        if not value:
            return {}
        return {"doi": {"identifier": value, "provider": "external"}}

    @model_validator(mode="before")
    def validate_complex_metadata(cls, values):
        """Validate and transform complex metadata fields."""
        access = {
            "record": values.get("access.record", "public"),
            "files": values.get("access.files", "public"),
        }
        embargo_active = values.get("access.embargo.active")
        embargo_until = values.get("access.embargo.until")
        embargo_reason = values.get("access.embargo.reason")

        if embargo_active or embargo_until or embargo_reason:
            access["embargo"] = {
                "active": embargo_active,
                "until": embargo_until,
                "reason": embargo_reason,
            }
        values["access"] = access
        values["metadata"] = MetadataSchema(**values)
        return values

    @model_validator(mode="before")
    def load_custom_fields(cls, values):
        """Load custom fields from config."""
        custom_fields = dict()
        config = current_app.config.get("BULK_IMPORTER_CUSTOM_FIELDS", {}).get(
            "csv_rdm_record_serializer", []
        )
        for t in config:
            result = obj_or_import_string(t["transformer"])(values)
            # only add to custom fields if the transformer returns a value
            if result:
                custom_fields[t["field"]] = result
        values["custom_fields"] = custom_fields
        return values


class CSVRDMRecordSerializer(CSVSerializer):
    """Serializer for RDM records."""

    def transform(self, obj: dict) -> tuple[dict | None, list[Error] | None]:
        """Transform the input object into a CSV-compatible format.

        Args:
            obj (dict): The input object to transform.
        Returns:
            dict: The transformed object.
        """
        try:
            return (
                CSVRecordSchema(**obj).model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                ),
                None,
            )
        except ValidationError as e:
            return None, generate_error_messages(e.errors())
