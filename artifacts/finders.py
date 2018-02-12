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
    def list(self):
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

    def package_depends_on_webpack(self, package_json_path):
        """
        """
        with self.storage.open(package_json_path) as package_json_file:
            package_json = json.loads(package_json_file.read())
            dependencies = package_json['dependencies'].keys()
            dev_dependencies = package_json['devDependencies'].keys()

        return ('webpack' in dependencies) or ('webpack' in dev_dependencies)

    def get_webpack_paths(self, webpack_root):
        """
        """
        _webpack_config = 'webpack.config.js'
        _webpack_config_path = os.path.join(webpack_root, _webpack_config)
        webpack_bin = 'node_modules/webpack/bin/webpack.js'
        webpack_config = _webpack_config if self.storage.exists(
            _webpack_config_path,
        ) else None

        return webpack_root, webpack_bin, webpack_config

    def list(self):
        """
        """
        directories, files = self.storage.listdir('')

        for directory in directories:
            package_json_path = os.path.join(directory, 'package.json')

            if self.storage.exists(package_json_path):
                if self.package_depends_on_webpack(package_json_path):
                    webpack_paths = self.get_webpack_paths(directory)

                    yield webpack_paths, self.storage


def get_webpack_finders():
    """
    """
    finders =  [
        get_finder(Finder) for Finder in artifacts_settings.WEBPACK_FINDERS
    ]

    yield from finders


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
