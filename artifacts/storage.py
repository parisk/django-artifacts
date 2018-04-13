from collections import OrderedDict
import functools
import os
import re

from azure.storage.blob import BlockBlobService
from django.conf import settings
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

from .finders import get_finders
from .settings import artifacts_settings


class ArtifactsStorage(ManifestStaticFilesStorage):
    """
    """

    def _sieve_paths(self, paths, ignore_patterns):
        """
        """
        for path in paths:
            should_not_be_ignored = not any(
                [re.match(pattern, path) for pattern in ignore_patterns],
            )
            if should_not_be_ignored:
                yield path

    def _sieve_paths_not_for_hashing(self, paths):
        """
        """
        yield from self._sieve_paths(
            paths.keys(), artifacts_settings.HASHING_IGNORE_PATTERNS,
        )

    @property
    def environments(self):
        """
        """
        for finder in get_finders():
            yield from finder.list()

    def build_artifacts(self):
        """
        """
        for environment in self.environments:
            artifacts = environment.build_artifacts()
            yield from [(environment, artifact) for artifact in artifacts]

    def post_process(self, paths, **options):
        """
        """
        next_paths = OrderedDict()

        for environment, artifact in self.build_artifacts():
            next_paths[artifact] = self, artifact

            # Below we are yielding: original_path, processed_path, processed
            yield environment.label, artifact, True

        for path in self._sieve_paths_not_for_hashing(paths):
            next_paths[path] = paths[path]

        yield from super().post_process(next_paths, **options)


class ArtifactsAzureStorage(ArtifactsStorage):
    """
    """
    account_name = artifacts_settings.AZURE_ACCOUNT_NAME
    account_key = artifacts_settings.AZURE_ACCOUNT_KEY
    azure_container = artifacts_settings.AZURE_CONTAINER
    azure_ssl = artifacts_settings.AZURE_SSL

    @property
    @functools.lru_cache()
    def connection(self):
        blob_service = BlockBlobService(self.account_name, self.account_key)
        return blob_service

    def post_process(self, paths, **options):
        """
        Uploads the given path to the Azure container defined in the settings.
        """
        paths_to_be_uploaded = super().post_process(paths, **options)

        for original_path, processed_path, processed in paths_to_be_uploaded:
            yield original_path, processed_path, processed

            print(f'Uploading to Azure: {processed_path}')

            self.connection.create_blob_from_path(
                self.azure_container,
                processed_path,
                os.path.join(settings.STATIC_ROOT, processed_path),
            )
