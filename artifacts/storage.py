from collections import OrderedDict
import os
import re

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

from . import builders
from . import finders


NODE_PATH = 'node'
WEBPACK_FINDERS = [
    'artifacts.finders.WebpackDirectoryAutoFinder',
]
IGNORE_PATTERNS = [
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
            matches = False

            for pattern in ignore_patterns:
                if re.match(pattern, path):
                    matches = True
                    break

            if not matches:
                yield path

    def post_process(self, paths, **options):
        """
        """
        _paths = OrderedDict()

        for finder in finders.get_finders(WEBPACK_FINDERS):
            for (directory, webpack_bin, config), storage in finder.list():
                working_dir = storage.path(directory)
                webpack_bin_path = os.path.join(working_dir, webpack_bin)

                if config:
                    config = os.path.join(working_dir, config)

                builder = builders.WebpackBuilder(
                    working_dir, webpack_bin_path, config, NODE_PATH,
                )
                builder.build()

                for artifact in builder.artifacts:
                    _paths[artifact] = self, artifact
                    original_path = f'[webpack build in {directory}]'
                    processed_path = artifact
                    processed = True
                    yield original_path, processed_path, processed

        for path in self._sieve_paths(paths.keys(), IGNORE_PATTERNS):
            _paths[path] = paths[path]

        yield from super().post_process(_paths, **options)
