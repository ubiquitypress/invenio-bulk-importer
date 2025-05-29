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
from flask import current_app
from google.cloud import storage
from invenio_communities.proxies import current_communities
from invenio_files_rest.models import ObjectVersion
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_records_resources.tasks import system_identity
from marshmallow.exceptions import ValidationError as MarshmallowValidationError

from invenio_bulk_importer.errors import Error


class RecordType(ABC):
    """Base serializer class."""

    def __init__(self, serializer_data: tuple[dict | None, list[Error]]):
        """Initialize the record type."""
        self._files: list[str] = (
            serializer_data[0].pop("files", []) if serializer_data[0] else []
        )
        self._communities: list[str] = (
            serializer_data[0].pop("communities", []) if serializer_data[0] else []
        )
        self._is_community_required = current_app.config.get(
            "RDM_COMMUNITY_REQUIRED_TO_PUBLISH", False
        )
        self._serializer_data: dict | None = (
            serializer_data[0] if serializer_data[0] else None
        )
        self._errors: list[Error] = serializer_data[1] if serializer_data[1] else []
        self._record: dict | None = None
        self.is_succssful = True

    @abstractmethod
    def validate(self) -> bool:
        """Load the stream object by object.

        :param stream: IO
        """

    # @abstractmethod
    # def run(self, obj: dict) -> dict:
    #     """Transform a given object into something Invenio understands."""

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


class RDMRecord(RecordType):
    """Base class for all CSV serializers."""

    def __init__(
        self, serializer_data: tuple[dict | None, dict | None], bucket_id: str, **kwargs
    ):
        """Initialize the resource.

        Args:
            serializer_data (tuple[dict | None, dict | None]): Data from the serializer [serialized record dict, errors].
            bucket_id (str): Identifier for the invenio bucket.
            **kwargs: Additional keyword arguments.
        """
        # Initialize the serializer data and errors
        super().__init__(serializer_data)
        self.bucket_id = bucket_id
        self.kwargs = kwargs

    def _verify_communities_exist(self, communities: list):
        """Verify that the listed communities exist."""
        # Implement community existence check logic here
        # For example, check against a database or an API
        if not communities and self._is_community_required:
            self._add_error(
                Error(
                    type="community_not_provided",
                    loc="communities",
                    msg="At least one community is required to publish the record.",
                )
            )
            return
        for community_slug in communities:
            try:
                current_communities.service.read(
                    id_=community_slug,
                    identity=system_identity,
                )
            except PIDDoesNotExistError:
                self._add_error(
                    Error(
                        type="community_not_found",
                        loc="communities",
                        msg=f"Community '{community_slug}' not found.",
                    )
                )

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

            storage_client = storage.Client()
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

            s3_client = boto3.client("s3")
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

    def _verify_rdm_record_correctness(self, serializer_data):
        """Verify that the RDM record is correct."""
        schema = current_rdm_records_service.schema
        try:
            self._record = schema.load(
                serializer_data,
                context={"identity": system_identity},
                raise_errors=True,
            )
        except MarshmallowValidationError as e:
            self._process_validation_errors(e.messages, prefix="")

    def _process_validation_errors(self, errors, prefix=""):
        """Process validation errors recursively.

        Args:
            errors: The validation errors dict or list
            prefix: The current field path prefix
        """
        if isinstance(errors, dict):
            # Handle dictionary of errors (field_name -> error_message)
            for field, error in errors.items():
                field_path = f"{prefix}.{field}" if prefix else field

                if isinstance(error, (dict, list)):
                    # Recursively process nested errors
                    self._process_validation_errors(error, field_path)
                else:
                    # Handle string or list of string errors
                    if isinstance(error, list):
                        for err_msg in error:
                            self._add_error(
                                Error(type="validation_error", loc=prefix, msg=error)
                            )
                    else:
                        self._add_error(
                            Error(type="validation_error", loc=prefix, msg=error)
                        )
        elif isinstance(errors, list):
            # Handle list of errors
            if all(isinstance(item, (dict, list)) for item in errors):
                # List of nested structures
                for i, error in enumerate(errors):
                    self._process_validation_errors(error, f"{prefix}[{i}]")
            else:
                # List of string error messages
                for error in errors:
                    self._add_error(
                        Error(type="validation_error", loc=prefix, msg=error)
                    )

    def validate(self) -> bool:
        """Validate the serializer object can be loaded into Invenio.

        Returns True if the validation is successful, otherwise False.
        """
        self._verify_files_accessible(self._files)
        self._verify_communities_exist(self._communities)
        self._verify_rdm_record_correctness(self._serializer_data)
        return self.is_succssful
