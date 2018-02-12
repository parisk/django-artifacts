from collections import OrderedDict
import os
import re

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

from . import builders, finders
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
    def _builders(self):
        """
        """
        for finder in finders.get_webpack_finders():
            for webpack_paths, storage in finder.list():
                webpack_root, webpack_bin, webpack_config = webpack_paths
                builder = builders.WebpackBuilder(
                    storage,
                    webpack_root,
                    webpack_bin,
                    webpack_config,
                    artifacts_settings.NODE_PATH,
                )
                yield builder

    def build_artifacts(self):
        """
        """
        for builder in self._builders:
            builder.build()

            yield from [(builder, artifact) for artifact in builder.artifacts]

    def post_process(self, paths, **options):
        """
        """
        _paths = OrderedDict()

        for builder, artifact in self._artifacts:
            _paths[artifact] = self, artifact
            original_path = f'[webpack build in {builder._webpack_root}]'
            processed_path = artifact
            processed = True
            yield original_path, processed_path, processed

        for path in self._sieve_paths_not_for_hashing(paths):
            _paths[path] = paths[path]

        yield from super().post_process(_paths, **options)
