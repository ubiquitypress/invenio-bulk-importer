# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Base serializer."""

import csv
from abc import ABC, abstractmethod
from typing import IO, Iterator


class Serializer(ABC):
    """Base serializer class."""

    @abstractmethod
    def load(self, stream: IO, **kwargs) -> Iterator[dict]:
        """Load the stream object by object.

        :param stream: IO
        """

    @abstractmethod
    def transform(self, obj: dict) -> tuple[dict | None, list[dict] | None]:
        """Transform a given object into dict Invenio understands."""


class CSVSerializer(Serializer):
    """Base class for all CSV serializers."""

    def _clean_row(self, row):
        """Remove empty strings replacing them wit `None` values."""
        return {k: v for k, v in row.items() if v != ""}

    def load(self, stream: IO, **kwargs) -> Iterator[dict]:
        """Load the content of the stream using ``DictReader``."""
        for row in csv.DictReader(stream, **kwargs):
            yield self._clean_row(row)
