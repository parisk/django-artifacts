from collections import OrderedDict
import os
import re

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

from . import environments, finders
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
        for finder in finders.get_finders():
            for webpack_paths, storage in finder.list():
                webpack_root, webpack_bin, webpack_config = webpack_paths
                environment = environments.WebpackBuildEnvironment(
                    storage,
                    webpack_root,
                    webpack_bin,
                    webpack_config,
                    artifacts_settings.NODE_PATH,
                )
                yield environment

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
