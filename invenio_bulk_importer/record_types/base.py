# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Base resource."""

from abc import ABC, abstractmethod
from urllib.parse import urlparse

import boto3
import requests
from botocore import UNSIGNED
from botocore.client import Config
from flask import current_app
from google.cloud import storage
from invenio_communities.proxies import current_communities
from invenio_files_rest.models import ObjectVersion
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_records_resources.tasks import system_identity

from invenio_bulk_importer.errors import Error


class RecordType(ABC):
    """Base record type class."""

    def __init__(self, serializer_data: tuple[dict | None, list[Error]]):
        """Initialize the record type."""
        self.id: str | None = (
            serializer_data[0].pop("id", None) if serializer_data[0] else None
        )
        self._serializer_record_data: dict | None = (
            serializer_data[0] if serializer_data[0] else None
        )
        self._errors: list[Error] = serializer_data[1] if serializer_data[1] else []
        self._record: dict | None = None
        self.is_succssful = True

    @abstractmethod
    def validate(self) -> bool:
        """Load the stream object by object."""

    @abstractmethod
    def run(self) -> dict:
        """Transform a given object into something Invenio understands."""

    @property
    def errors(self) -> list[Error]:
        """Return the list of errors."""
        return self._errors

    def _add_error(self, error: Error) -> None:
        """Add an error to the errors list."""
        if not isinstance(error, Error):
            raise TypeError("Error must be an instance of ErrorMessage.")
        self._errors.append(error)
        self.is_succssful = False


class CommunityMixin:
    """Mixin to handle community-related operations."""

    def _add_community_vars(self, serializer_data: tuple[dict | None, list[Error]]):
        """Initialize the mixin with serializer data."""
        self._serializer_communities: list[str] = (
            serializer_data[0].pop("communities", []) if serializer_data[0] else []
        )
        self._is_community_required = current_app.config.get(
            "RDM_COMMUNITY_REQUIRED_TO_PUBLISH", False
        )
        self._community_uuids: dict[str, str | list[str]] = dict(default=None, ids=[])

    def _verify_communities_exist(self, communities: list):
        """Verify that the listed communities exist."""
        if not communities and self._is_community_required:
            self._add_error(
                Error(
                    type="community_not_provided",
                    loc="communities",
                    msg="At least one community is required to publish the record.",
                )
            )
            return
        for idx, community_slug in enumerate(communities):
            try:
                community = current_communities.service.read(
                    id_=community_slug,
                    identity=system_identity,
                )
                if idx == 0:
                    self._community_uuids["default"] = community.id
                self._community_uuids["ids"].append(community.id)
            except PIDDoesNotExistError:
                self._add_error(
                    Error(
                        type="community_not_found",
                        loc="communities",
                        msg=f"Community '{community_slug}' not found.",
                    )
                )


class FileMixin:
    """Mixin to handle file-related operations."""

    def _add_file_vars(
        self, serializer_data: tuple[dict | None, list[Error]], bucket_id: str
    ):
        """Initialize the mixin with serializer data."""
        self._files: list[str] = (
            serializer_data[0].pop("files", []) if serializer_data[0] else []
        )
        self.bucket_id = bucket_id

    def _check_url_file_accessibility(self, file: str):
        """Check if the URL file is accessible."""
        try:
            response = requests.head(file, timeout=10)
            if response.status_code >= 400:
                self._add_error(
                    Error(
                        type="file_not_accessible",
                        loc="files",
                        msg=f"Error accessing URL file '{file}' returned status code {response.status_code}.",
                    )
                )
        except Exception as e:
            self._add_error(
                Error(
                    type="file_not_accessible",
                    loc="files",
                    msg=f"Error accessing URL file '{file}': {str(e)}",
                )
            )

    def _check_gs_file_accessibility(self, file: str):
        """Check if the Google Cloud Storage file is accessible."""
        try:
            parsed_url = urlparse(file)
            bucket_name = parsed_url.netloc
            blob_name = parsed_url.path.lstrip("/")

            storage_client = storage.Client.create_anonymous_client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            if not blob.exists():
                self._add_error(
                    Error(
                        type="file_not_accessible",
                        loc="files",
                        msg=f"Error accessing GCS file '{file}' does not exist.",
                    )
                )
        except Exception as e:
            self._add_error(
                Error(
                    type="file_not_accessible",
                    loc="files",
                    msg=f"Error accessing GCS file '{file}': {str(e)}",
                )
            )

    def _check_s3_file_accessibility(self, file: str):
        """Check if the S3 file is accessible."""
        try:
            parsed_url = urlparse(file)
            bucket_name = parsed_url.netloc
            key = parsed_url.path.lstrip("/")

            s3_client = boto3.client(
                "s3",
                config=Config(signature_version=UNSIGNED),
            )
            s3_client.head_object(Bucket=bucket_name, Key=key)
        except Exception as e:
            self._add_error(
                Error(
                    type="file_not_accessible",
                    loc="files",
                    msg=f"Error accessing S3 file '{file}': {str(e)}",
                )
            )

    def _verify_files_accessible(self, files: list) -> bool:
        """Verify that the listed files are accessible."""
        # Get list of files in the bucket
        object_versions = [
            obj_ver.basename for obj_ver in ObjectVersion.get_by_bucket(self.bucket_id)
        ]
        for file in files:
            # HTTP/HTTPS URL
            if file.startswith(("http://", "https://")):
                self._check_url_file_accessibility(file)
            # S3 cloud storage
            elif file.startswith("s3:"):
                self._check_s3_file_accessibility(file)
            # Google Cloud Storage
            elif file.startswith("gs:"):
                self._check_gs_file_accessibility(file)
            # Local file in bucket
            else:
                if file not in object_versions:
                    self._add_error(
                        Error(
                            type="file_not_found",
                            loc="files",
                            msg=f"File '{file}' not found in invenio bucket.",
                        )
                    )


class InvenioRecordMixin:
    """Mixin to handle Invenio record-related operations."""

    def _verify_record_exists(self, record_id: str) -> bool:
        """Verify that the draft or published record exist."""
        if not record_id:
            return True  # No record ID provided, nothing to verify

        try:
            current_rdm_records_service.read(system_identity, record_id)
        except Exception:
            try:
                current_rdm_records_service.read_draft(system_identity, record_id)
            except Exception:
                self._add_error(
                    Error(
                        type="existing_record_not_found",
                        loc="record",
                        msg=f"Record '{record_id}' not found.",
                    )
                )
                return False
        return True
