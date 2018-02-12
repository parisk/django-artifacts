from collections import OrderedDict
import os
import re

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

from . import builders
from . import finders


NODE_PATH = 'node'
WEBPACK_FINDERS = [
    'artifacts.finders.WebpackAutoFinder',
]
HASHING_IGNORE_PATTERNS = [
    r'.*/node_modules/.*',
    r'.*/package(-lock)?\.json$',
    r'.*/yarn\.lock$',
]


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

    def post_process(self, paths, **options):
        """
        """
        _paths = OrderedDict()

        for finder in finders.get_finders(WEBPACK_FINDERS):
            for webpack_paths, storage in finder.list():
                webpack_root, webpack_bin, webpack_config = webpack_paths
                builder = builders.WebpackBuilder(
                    storage,
                    webpack_root,
                    webpack_bin,
                    webpack_config,
                    NODE_PATH,
                )
                builder.build()

                for artifact in builder.artifacts:
                    _paths[artifact] = self, artifact
                    original_path = f'[webpack build in {webpack_root}]'
                    processed_path = artifact
                    processed = True
                    yield original_path, processed_path, processed

        for path in self._sieve_paths(paths.keys(), HASHING_IGNORE_PATTERNS):
            _paths[path] = paths[path]

        yield from super().post_process(_paths, **options)
