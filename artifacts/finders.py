import functools
import json
import os

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.utils.module_loading import import_string

from .settings import artifacts_settings


class BaseFinder:
    """
    A base file finder to be used for custom artifacts finder classes.
    """
    def list(self, ignore_patterns):
        """
        Given an optional list of paths to ignore, return a two item iterable
        consisting of the relative path and storage instance.
        """
        msg = 'subclasses of BaseFinder must provide a list() method'
        raise NotImplementedError(msg)


class WebpackAutoFinder(BaseFinder):
    """
    ...
    """
    def __init__(self, storage=None):
        self.storage = storage or StaticFilesStorage()

    def list(self):
        directories, files = self.storage.listdir('')

        for directory in directories:
            package_json_path = os.path.join(directory, 'package.json')

            if self.storage.exists(package_json_path):
                package_json_contents = self.storage.open(package_json_path)
                package_json = json.loads(package_json_contents.read())
                dependencies = package_json['dependencies'].keys()
                dev_dependencies = package_json['devDependencies'].keys()
                webpack_in_dependencies = 'webpack' in dependencies
                webpack_in_dev_dependencies = 'webpack' in dev_dependencies

                if (webpack_in_dependencies or webpack_in_dev_dependencies):
                    webpack_working_dir = self.storage.path(directory)
                    webpack_bin = 'node_modules/webpack/bin/webpack.js'
                    webpack_configuration = None
                    webpack_configuration_path = 'webpack.config.js'

                    if self.storage.exists(webpack_configuration_path):
                        webpack_configuration = webpack_configuration_path

                    paths = directory, webpack_bin, webpack_configuration

                    yield paths, self.storage


def get_webpack_finders():
    """
    """
    yield from [
        get_finder(Finder) for Finder in artifacts_settings.WEBPACK_FINDERS
    ]


@functools.lru_cache(maxsize=None)
def get_finder(Finder):
    """
    Return an instance of the given Finder class, after verifying that it is
    a subclass of BaseFinder
    """
    if not issubclass(Finder, BaseFinder):
        msg = f'Finder "{Finder}" is not a subclass of "{BaseFinder}"'
        raise ImproperlyConfigured(msg)
    return Finder()
