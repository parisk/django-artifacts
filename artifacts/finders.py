import functools
import json
import os

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.utils.module_loading import import_string

from . import environments
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

    def list(self):
        """
        """
        directories, files = self.storage.listdir('')

        for directory in directories:
            package_json_path = os.path.join(directory, 'package.json')

            if self.storage.exists(package_json_path):
                if self.package_depends_on_webpack(package_json_path):
                    environment = environments.WebpackBuildEnvironment(
                        self.storage, directory,
                    )
                    yield environment


def get_finders():
    """
    """
    finder_classes = artifacts_settings.BUILD_ENVIRONMENT_FINDERS
    yield from [get_finder(finder_class) for finder_class in finder_classes]


@functools.lru_cache(maxsize=None)
def get_finder(finder_class):
    """
    Return an instance of the given `finder_class`, after verifying that it is
    a subclass of BaseFinder.
    """
    if not issubclass(finder_class, BaseFinder):
        msg = f'Finder "{Finder}" is not a subclass of "{BaseFinder}"'
        raise ImproperlyConfigured(msg)

    return finder_class()
