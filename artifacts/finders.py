import functools
import json
import os

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.utils.module_loading import import_string


class BaseFinder:
    """
    A base file finder to be used for custom artifacts finder classes.
    """
    def check(self, **kwargs):
        raise NotImplementedError(
            'subclasses may provide a check() method to verify the finder is '
            'configured correctly.'
        )

    def find(self, path, all=False):
        """
        Given a relative file path, find an absolute file path.
        If the ``all`` parameter is False (default) return only the first
        found file path; if True, return a list of all found files paths.
        """
        msg = 'subclasses of BaseFinder must provide a find() method'
        raise NotImplementedError(msg)

    def list(self, ignore_patterns):
        """
        Given an optional list of paths to ignore, return a two item iterable
        consisting of the relative path and storage instance.
        """
        msg = 'subclasses of BaseFinder must provide a list() method'
        raise NotImplementedError(msg)


class WebpackDirectoryAutoFinder(BaseFinder):
    """
    A static files finder that uses the ``WEBPACK_DIRS`` setting
    to locate files.
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


def get_finders(finder_path_list):
    """
    ...
    """
    for finder_path in finder_path_list:
        yield get_finder(finder_path)


@functools.lru_cache(maxsize=None)
def get_finder(import_path):
    """
    Import the artifacts finder class described by import_path, where
    import_path is the full Python path to the class.
    """
    Finder = import_string(import_path)
    if not issubclass(Finder, BaseFinder):
        msg = f'Finder "{Finder}" is not a subclass of "{BaseFinder}"'
        raise ImproperlyConfigured(msg)
    return Finder()
