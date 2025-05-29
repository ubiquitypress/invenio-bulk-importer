"""Imprint specific custom fields.

This is highly "inspired by" invenio_rdm_records.contrib.imprint

Implements the following fields:

- imprint:imprint.title
- imprint:imprint.isbn
- imprint:imprint.pages
- imprint:imprint.place
- imprint:imprint.edition
- imprint:imprint.volume
"""

from idutils import is_isbn
from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.resources.serializers.ui.schema import AdditionalTitlesSchema
from invenio_rdm_records.services.schemas.metadata import TitleSchema
from marshmallow import fields, validate
from marshmallow_utils.fields import SanitizedUnicode

from .base import CustomVocabularyField


def _valid_url(error_msg):
    """Return a URL validation rule with custom error message."""
    return validate.URL(error=error_msg)


class Imprint(CustomVocabularyField):
    """Nested custom field."""

    def __init__(self, name, field_args=None):
        """Initialize."""
        super().__init__(name, "titletypes", field_args)

    @property
    def field(self):
        """Imprint fields definitions."""
        return fields.Nested(
            {
                "title": SanitizedUnicode(),
                "alternative_titles": fields.List(fields.Nested(TitleSchema)),
                "isbn": SanitizedUnicode(
                    validate=is_isbn,
                    error_messages={
                        "validator_failed": [_("Please provide a valid ISBN.")]
                    },
                ),
                "pages": SanitizedUnicode(),
                "place": SanitizedUnicode(),
                "edition": SanitizedUnicode(),
                "volume": SanitizedUnicode(),
                "series_name": SanitizedUnicode(),
                "buy_book": SanitizedUnicode(
                    validate=_valid_url(_("Not a valid URL."))
                ),
            }
        )

    @property
    def field_ui(self):
        """Imprint field definitions for the UI."""
        schema = self.field
        schema["alternative_titles"] = fields.List(
            fields.Nested(AdditionalTitlesSchema)
        )
        return schema

    @property
    def mapping(self):
        """Imprint search mappings."""
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "alternative_titles": {
                    "properties": {
                        "lang": {
                            "type": "object",
                            "properties": {
                                "@v": {"type": "keyword"},
                                "id": {"type": "keyword"},
                                "title": {"type": "object", "dynamic": "true"},
                            },
                        },
                        "title": {
                            "type": "text",
                            "fields": {"keyword": {"type": "keyword"}},
                        },
                        "type": {
                            "type": "object",
                            "properties": {
                                "@v": {"type": "keyword"},
                                "id": {"type": "keyword"},
                                "title": {"type": "object", "dynamic": "true"},
                            },
                        },
                    }
                },
                "isbn": {"type": "keyword"},
                "pagination": {"type": "keyword"},
                "place": {"type": "keyword"},
                "edition": {"type": "keyword"},
                "volume": {"type": "keyword"},
                "series_name": {"type": "keyword"},
                "buy_book": {"type": "keyword"},
            },
        }


IMPRINT_CUSTOM_FIELDS = [
    Imprint(name="imprint:imprint"),
]

IMPRINT_CUSTOM_FIELDS_UI = {
    "section": _("Book / Report / Chapter"),
    "hide_from_upload_form": False,
    "discoverable_fields": False,
    "displaySection": True,
    "formSection": "publishing",
    "resourceTypes": [
        "publication-book",
        "publication-book-chapter",
        "presentation",
        "open-educational-resource",
        "map",
        "publication-report",
    ],
    "fields": [
        {
            "field": "imprint:imprint",
            "ui_widget": "ImprintField",
            "template": "imprint.html",
            "props": {
                "label": _("Imprint (Book, Chapter, or Report)"),
                "place": {
                    "label": _("Place"),
                    "placeholder": _("e.g. city, country"),
                    "description": _("Place where the book or report was published"),
                },
                "isbn": {
                    "label": _("ISBN"),
                    "placeholder": _("e.g. 0-06-251587-X"),
                    "description": _("International Standard Book Number"),
                },
                "title": {
                    "label": _("Book or report title"),
                    "placeholder": "",
                    "description": _(
                        "Title of the book or report which this upload is part of"
                    ),
                },
                "pages": {
                    "label": _("Pagination"),
                    "placeholder": _("e.g. 15-23 or 158"),
                    "description": "",
                },
                "icon": "book",
            },
        },
    ],
}
