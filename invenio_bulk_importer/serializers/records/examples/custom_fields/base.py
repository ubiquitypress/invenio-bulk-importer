"""Custom Vocabulary base field.

This fields kind of supports vocabulary fields as subfields by tricking the custom
field engine into thinking it really is a vocabulary field.
"""

from flask import current_app
from invenio_i18n.ext import current_i18n
from invenio_records_resources.records.systemfields import PIDRelation
from invenio_records_resources.services.custom_fields import BaseCF
from invenio_vocabularies.proxies import current_service as current_vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from marshmallow_utils.fields.babel import gettext_from_dict


class CustomVocabularyField(BaseCF):
    """Custom field base class for fields with a vocabulary subfield."""

    field_keys = ["id", "props", "title", "icon"]

    def __init__(self, name, vocabulary_id, field_args=None, relation_cls=None):
        """Initialize the field."""
        super().__init__(name, field_args)
        # Trick Invenio into thinking this is a vocabulary field
        self.relation_cls = relation_cls or PIDRelation
        self.vocabulary_id = vocabulary_id
        self.pid_field = Vocabulary.pid.with_type_ctx(self.vocabulary_id)

        # Utilities

    def _get_label(self, hit):
        """Return label (translated title) of hit."""
        return gettext_from_dict(
            hit["title"],
            current_i18n.locale,
            current_app.config.get("BABEL_DEFAULT_LOCALE", "en"),
        )

    def options(self, identity):
        """Return UI serialized vocabulary items."""
        results = current_vocabulary_service.read_all(
            identity,
            fields=self.field_keys,
            type=self.vocabulary_id,
        )
        return [
            {
                "text": self._get_label(hit),
                "value": hit["id"],
            }
            for hit in results.to_dict()["hits"]["hits"]
        ]
