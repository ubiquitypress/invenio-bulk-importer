"""CSV serializer for RDM records."""

from typing import Annotated, Dict, List, Literal, Optional, Union

from pydantic import BeforeValidator, BaseModel, Field, field_validator, model_validator

from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.tasks import system_identity

from invenio_bulk_importer.serializers.base import CSVSerializer


def ensure_new_line_list(value: str) -> list:
    if value is None:
        return []
    return [v.strip() for v in value.split("\n")]


# Custom field to handle newline-separated lists
NewlineList = Annotated[list[str], BeforeValidator(ensure_new_line_list), Field(default_factory=list)]


class BaseIdentifier(BaseModel):
    """Schema for identifiers."""

    scheme: str | None = Field(default=None)
    identifier: str | None = Field(default=None)


class FullIdentifier(BaseIdentifier):
    """Schema for full identifiers."""

    resource_type: dict[str, str | None] = Field(default_factory=dict)
    relation_type: dict[str, str | None] = Field(default_factory=dict)


class Affiliation(BaseModel):
    """Schema for affiliation."""

    id: str | None = Field(default=None)
    name: str | None = Field(default=None)


class PersonOrOrg(BaseModel):
    """Schema for person or organization."""

    family_name: str | None = Field(default=None)
    given_name: str | None = Field(default=None)
    name: str | None = Field(default=None)
    type: Literal["personal", "organizational"]
    identifiers: List[BaseIdentifier] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_fields_based_on_type(self):
        """Validate fields based on the value of 'type'."""
        person_type = self.type
        if person_type == "organizational" and not self.name:
            raise ValueError("An organizational person must have 'name' filled in.")
        if person_type == "personal" and not self.family_name:
            raise ValueError("A personal person must have 'family_name' filled in.")
        return self


CreatibutorList = Annotated[list[dict[str, Union[PersonOrOrg, list[Affiliation]]]], Field(default_factory=list)]


class CsvBaseSchema(BaseModel):
    
    @staticmethod
    def process_grouped_fields(original: dict, prefix: str) -> list:
        """Process grouped fields in the input dictionary.
        Args:
            original (dict): The original dictionary containing grouped fields.
            prefix (str): The prefix used to identify the grouped fields.
        Returns:
            list: A list of dictionaries representing the grouped fields.
        """
        group_input = {
            key: value
            for key, value in original.items()
            if key.startswith(f"{prefix}.")
        }
        # Get a temporary list of item information for easier working.
        num_people = max(len(value.split("\n")) for value in group_input.values())
        output = []
        keys = group_input.keys()
        for i in range(num_people):
            item_dict = {}
            for key in keys:
                parts = key.split(".") 
                values = group_input[key].split("\n")
                item_dict[".".join(parts[1:])] = values[i] if i < len(values) and values[i].strip() else None
            output.append(item_dict)
        return output


class MetadataSchema(CsvBaseSchema):
    """Schema for handling metadata fields."""

    title: str
    publication_date: str
    description: str
    version: str
    publisher: str
    resource_type: dict[str, str] = Field(default_factory=list, alias="resource_type.id")
    languages: list[dict[str, str]] = Field(default_factory=list, alias="languages.id")
    creators: CreatibutorList
    contributors: CreatibutorList
    additional_descriptions: list[dict[str, Union[str, dict[str, str]]]] = Field(default_factory=list)
    subjects: list[dict[str, str]] = Field(default_factory=list)
    references: list[dict[str, str]] = Field(default_factory=list, alias="references.reference")
    identifiers: list[BaseIdentifier] = Field(default_factory=list)
    related_identifiers: list[FullIdentifier] = Field(default_factory=list)
    # rights

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
        return [{"reference": reference.strip()} for reference in value.split("\n") if reference.strip()]

    @model_validator(mode="before")
    def load_identifiers(cls, values):
        """Load identifiers."""
        temp_out = cls.process_grouped_fields(values, "identifiers")
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
        temp_out = cls.process_grouped_fields(values, "related_identifiers")
        # print(temp_out)
        output = []
        for identifier in temp_out:
            output.append(
                {
                    "identifier": identifier.get("identifier"),
                    "scheme": identifier.get("scheme"),
                    "relation_type": {
                        "id": identifier.get("relation_type.id"),
                    },
                    "resource_type": {
                        "id": identifier.get("resource_type.id"),
                    },
                }
            )
        print(output)
        values["related_identifiers"] = output
        return values

    @model_validator(mode="before")
    def load_additional_description(cls, values):
        """Load addictional desciptions."""
        output = []
        for key, value in values.items():
            if key.startswith("description.") and value:
                _, *modifiers = key.split(".")
                info = {"type": {"id": modifiers[0]}}
                if len(modifiers) == 2:
                    # We have language information, i.e. "desciption.abstract.eng"
                    info["lang"] = {"id": modifiers[1]}
                output.append({"description": value, **info})
        values["additional_descriptions"] = output
        return values

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
            temp_output = cls.process_grouped_fields(original, creatibutor_type)
            # Construct expected structures
            output = []
            for person in temp_output:
                # Construct person_or_org
                person_or_org = {
                    "type": person.get("type"),
                    "family_name": person.get("family_name"),
                    "given_name": person.get("given_name"),
                    "name": person.get("name")
                }
                person_or_org["identifiers"] = []
                # Extract all keys that start with 'identifiers.'
                identifier_keys = [key for key in person.keys() if key.startswith("identifiers.")]
                for key in identifier_keys:
                    scheme = key.split(".")[1]  # Extract the scheme from the key
                    if val := person.get(key):
                        person_or_org["identifiers"].append(
                            {"scheme": scheme, "identifier": val}
                        )
                # Construct affiliations
                affiliations = []
                aff_names = person.get("affiliations.name", "").split(";") if person.get("affiliations.name") else []
                aff_ids = person.get("affiliations.id", "").split(";") if person.get("affiliations.id") else []
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
                output.append({"person_or_org": person_or_org, "affiliations": affiliations})
            print(output)
            return output

        values["creators"] = load_creatibutor(values, "creators")
        values["contributors"] = load_creatibutor(values, "contributors")
        return values


class CSVRecordSchema(BaseModel):
    """CSV RDM Record Pydantic schema."""

    # pids: dict[]
    # {"pids": {"doi": {"identifier": doi_value, "provider": "external"}}}
    default_community: str = Field(default=None)
    communities: NewlineList
    files: NewlineList = Field(alias="filenames")
    access: dict[str, str | dict[str, str | None]]
    custom_fields: dict[str, str] = Field(default_factory=dict)
    metadata: MetadataSchema

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
        values["custom_fields"] = {}
        values["metadata"] = MetadataSchema(**values)
        return values


class CSVRDMRecordSerializer(CSVSerializer):
    """Serializer for RDM records."""

    def transform(self, obj: dict) -> dict:
        """Transform the input object into a CSV-compatible format.
        Args:
            obj (dict): The input object to transform.
        Returns:
            dict: The transformed object.
        """
        return CSVRecordSchema(**obj).model_dump(exclude_unset=True)
