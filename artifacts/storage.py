from collections import OrderedDict
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

from . import builders


WEBPACK_DIRS = [
    'web',
]


class ArtifactsStorage(ManifestStaticFilesStorage):
    """
    """
    def post_process(self, paths, **options):
        """
        """
        _paths = OrderedDict()

        for path in WEBPACK_DIRS:
            webpack_dir_path = self.path(path)
            builder = builders.WebpackBuilder(webpack_dir_path)
            builder.run()

            for artifact in builder.artifacts:
                _paths[artifact] = (self, artifact)
                original_path = f'(webpack build at {path})'
                processed_path = artifact
                processed = True
                yield original_path, processed_path, processed

        for path in paths.keys():
            if '/node_modules/' not in path:
                _paths[path] = paths[path]

        yield from super().post_process(_paths, **options)
