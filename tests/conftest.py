# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""General fixtures."""

from collections import namedtuple

import pytest
from invenio_access.permissions import system_identity
from invenio_app.factory import create_api
from invenio_notifications.services.builders import NotificationBuilder
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.subjects.api import Subject
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from invenio_bulk_importer.serializers.records.csv import CSVRDMRecordSerializer
from invenio_bulk_importer.serializers.records.examples.custom_fields.imprint import (
    IMPRINT_CUSTOM_FIELDS,
)


@pytest.fixture(scope="module")
def create_app():
    """Create app."""
    return create_api


@pytest.fixture(scope="module")
def app_config(app_config):
    """Overwrite pytest invenio app_config fixture."""
    app_config["RECORDS_REFRESOLVER_CLS"] = (
        "invenio_records.resolver.InvenioRefResolver"
    )
    app_config["RECORDS_REFRESOLVER_STORE"] = (
        "invenio_jsonschemas.proxies.current_refresolver_store"
    )
    app_config["JSONSCHEMAS_HOST"] = "not-used"
    app_config["THEME_FRONTPAGE"] = False
    app_config["BULK_IMPORTER_CUSTOM_FIELDS"] = {
        "csv_rdm_record_serializer": [
            {
                "field": "imprint:imprint",
                "transformer": "invenio_bulk_importer.serializers.records.examples.transformers.imprint_transform",
            }
        ]
    }
    app_config["BULK_IMPORTER_RECORD_TYPES"] = {
        "rdm_record_type": {
            "options": {
                "doi_minting": False,
                "publish": True,
            },
            "serializers": [CSVRDMRecordSerializer],
        }
    }
    app_config["RDM_NAMESPACES"] = {"imprint": None}
    app_config["RDM_CUSTOM_FIELDS"] = IMPRINT_CUSTOM_FIELDS
    app_config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"] = True
    return app_config


# Vocabularies


@pytest.fixture(scope="module")
def languages_type(app):
    """Lanuage vocabulary type."""
    return vocabulary_service.create_type(system_identity, "languages", "lng")


@pytest.fixture(scope="module")
def languages_v(app, languages_type):
    """Language vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "dan",
            "title": {
                "en": "Danish",
                "da": "Dansk",
            },
            "props": {"alpha_2": "da"},
            "tags": ["individual", "living"],
            "type": "languages",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {
                "en": "English",
                "da": "Engelsk",
            },
            "tags": ["individual", "living"],
            "type": "languages",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "dataset",
            "icon": "table",
            "props": {
                "csl": "dataset",
                "datacite_general": "Dataset",
                "datacite_type": "",
                "openaire_resourceType": "21",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Dataset",
                "subtype": "",
                "type": "dataset",
                "marc21_type": "dataset",
                "marc21_subtype": "",
            },
            "title": {"en": "Dataset"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {  # create base resource type
            "id": "image",
            "props": {
                "csl": "figure",
                "datacite_general": "Image",
                "datacite_type": "",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/ImageObject",
                "subtype": "",
                "type": "image",
                "marc21_type": "image",
                "marc21_subtype": "",
            },
            "icon": "chart bar outline",
            "title": {"en": "Image"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {  # create base resource type
            "id": "software",
            "props": {
                "csl": "figure",
                "datacite_general": "Software",
                "datacite_type": "",
                "openaire_resourceType": "0029",
                "openaire_type": "software",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/SoftwareSourceCode",
                "subtype": "",
                "type": "image",
                "marc21_type": "software",
                "marc21_subtype": "",
            },
            "icon": "code",
            "title": {"en": "Software"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "image-photo",
            "props": {
                "csl": "graphic",
                "datacite_general": "Image",
                "datacite_type": "Photo",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Photograph",
                "subtype": "image-photo",
                "type": "image",
                "marc21_type": "image",
                "marc21_subtype": "photo",
            },
            "icon": "chart bar outline",
            "title": {"en": "Photo"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def title_type(app):
    """title vocabulary type."""
    return vocabulary_service.create_type(system_identity, "titletypes", "ttyp")


@pytest.fixture(scope="module")
def title_type_v(app, title_type):
    """Title Type vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "subtitle",
            "props": {"datacite": "Subtitle"},
            "title": {"en": "Subtitle"},
            "type": "titletypes",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "alternative-title",
            "props": {"datacite": "AlternativeTitle"},
            "title": {"en": "Alternative title"},
            "type": "titletypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def description_type(app):
    """title vocabulary type."""
    return vocabulary_service.create_type(system_identity, "descriptiontypes", "dty")


@pytest.fixture(scope="module")
def description_type_v(app, description_type):
    """Title Type vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "methods",
            "title": {"en": "Methods"},
            "props": {"datacite": "Methods"},
            "type": "descriptiontypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def subject_v(app):
    """Subject vocabulary record."""
    subjects_service = current_service_registry.get("subjects")
    vocab = subjects_service.create(
        system_identity,
        {
            "id": "http://id.nlm.nih.gov/mesh/A-D000007",
            "scheme": "MeSH",
            "subject": "Abdominal Injuries",
        },
    )

    Subject.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def date_type(app):
    """Date vocabulary type."""
    return vocabulary_service.create_type(system_identity, "datetypes", "dat")


@pytest.fixture(scope="module")
def date_type_v(app, date_type):
    """Subject vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "other",
            "title": {"en": "Other"},
            "props": {"datacite": "Other", "marc": "oth"},
            "type": "datetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def contributors_role_type(app):
    """Contributor role vocabulary type."""
    return vocabulary_service.create_type(system_identity, "contributorsroles", "cor")


@pytest.fixture(scope="module")
def contributors_role_v(app, contributors_role_type):
    """Contributor role vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "datamanager",
            "props": {"datacite": "DataManager"},
            "title": {"en": "Data manager"},
            "type": "contributorsroles",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "projectmanager",
            "props": {"datacite": "ProjectManager"},
            "title": {"en": "Project manager"},
            "type": "contributorsroles",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "other",
            "props": {"datacite": "Other", "marc": "oth"},
            "title": {"en": "Other"},
            "type": "contributorsroles",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def relation_type(app):
    """Relation type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "relationtypes", "rlt")


@pytest.fixture(scope="module")
def relation_types_v(app, relation_type):
    """Relation type vocabulary record."""
    vocab1 = vocabulary_service.create(
        system_identity,
        {
            "id": "iscitedby",
            "props": {"datacite": "IsCitedBy"},
            "title": {"en": "Is cited by"},
            "type": "relationtypes",
        },
    )

    vocab2 = vocabulary_service.create(
        system_identity,
        {
            "id": "hasmetadata",
            "props": {"datacite": "HasMetadata"},
            "title": {"en": "Has metadata"},
            "type": "relationtypes",
        },
    )

    Vocabulary.index.refresh()

    return [vocab1, vocab2]


@pytest.fixture(scope="module")
def licenses(app):
    """Licenses vocabulary type."""
    return vocabulary_service.create_type(system_identity, "licenses", "lic")


@pytest.fixture(scope="module")
def licenses_v(app, licenses):
    """Licenses vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "cc-by-4.0",
            "props": {
                "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
                "scheme": "spdx",
                "osi_approved": "",
            },
            "title": {"en": "Creative Commons Attribution 4.0 International"},
            "tags": ["recommended", "all"],
            "description": {
                "en": "The Creative Commons Attribution license allows"
                " re-distribution and re-use of a licensed work on"
                " the condition that the creator is appropriately credited."
            },
            "type": "licenses",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def affiliations_v(app):
    """Affiliation vocabulary record."""
    affiliations_service = current_service_registry.get("affiliations")
    aff = affiliations_service.create(
        system_identity,
        {
            "id": "cern",
            "name": "CERN",
            "acronym": "CERN",
            "identifiers": [
                {
                    "scheme": "ror",
                    "identifier": "01ggx4157",
                },
                {
                    "scheme": "isni",
                    "identifier": "000000012156142X",
                },
            ],
        },
    )

    Affiliation.index.refresh()

    return aff


@pytest.fixture(scope="module")
def funders_v(app):
    """Funder vocabulary record."""
    funders_service = current_service_registry.get("funders")
    funder = funders_service.create(
        system_identity,
        {
            "id": "00k4n6c32",
            "identifiers": [
                {
                    "identifier": "000000012156142X",
                    "scheme": "isni",
                },
                {
                    "identifier": "00k4n6c32",
                    "scheme": "ror",
                },
            ],
            "name": "European Commission",
            "title": {
                "en": "European Commission",
                "fr": "Commission européenne",
            },
            "country": "BE",
        },
    )

    Funder.index.refresh()

    return funder


@pytest.fixture(scope="module")
def awards_v(app, funders_v):
    """Funder vocabulary record."""
    awards_service = current_service_registry.get("awards")
    award = awards_service.create(
        system_identity,
        {
            "id": "00k4n6c32::755021",
            "identifiers": [
                {
                    "identifier": "https://cordis.europa.eu/project/id/755021",
                    "scheme": "url",
                }
            ],
            "number": "755021",
            "title": {
                "en": (
                    "Personalised Treatment For Cystic Fibrosis Patients With "
                    "Ultra-rare CFTR Mutations (and beyond)"
                ),
            },
            "funder": {"id": "00k4n6c32"},
            "acronym": "HIT-CF",
            "program": "H2020",
        },
    )

    Award.index.refresh()

    return award


RunningApp = namedtuple(
    "RunningApp",
    [
        "app",
        "location",
        "cache",
        "resource_type_v",
        "subject_v",
        "languages_v",
        "affiliations_v",
        "title_type_v",
        "description_type_v",
        "date_type_v",
        "contributors_role_v",
        "relation_types_v",
        "licenses_v",
        "funders_v",
        "awards_v",
    ],
)


@pytest.fixture
def running_app(
    app,
    location,
    cache,
    resource_type_v,
    subject_v,
    languages_v,
    affiliations_v,
    title_type_v,
    description_type_v,
    date_type_v,
    contributors_role_v,
    relation_types_v,
    licenses_v,
    funders_v,
    awards_v,
):
    """This fixture provides an app with the typically needed db data loaded.

    All of these fixtures are often needed together, so collecting them
    under a semantic umbrella makes sense.
    """
    return RunningApp(
        app,
        location,
        cache,
        resource_type_v,
        subject_v,
        languages_v,
        affiliations_v,
        title_type_v,
        description_type_v,
        date_type_v,
        contributors_role_v,
        relation_types_v,
        licenses_v,
        funders_v,
        awards_v,
    )
