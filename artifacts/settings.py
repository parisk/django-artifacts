"""
Settings for Artifacts are all namespaced in the ARTIFACTS setting.
For example your project's `settings.py` file might look like this:

ARTIFACTS = {
    'BUILD_ENVIRONMENT_FINDERS': [
        'artifacts.finders.WebpackAutoFinder',
    ],
    'HASHING_IGNORE_PATTERNS': [
        r'.*/node_modules/.*',
        r'.*/package(-lock)?\.json$',
        r'.*/yarn\.lock$',
    ],
}

This module provides the `api_setting` object, that is used to access
REST framework settings, checking for user settings first, then falling
back to the defaults.
"""
import functools

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string


DEFAULTS = {
    'HASHING_IGNORE_PATTERNS': [
        r'.*/node_modules/.*',
        r'.*/package(-lock)?\.json$',
        r'.*/yarn\.lock$',
    ],
    'NODE_PATH': 'node',
    'BUILD_ENVIRONMENT_FINDERS': [
        'artifacts.finders.WebpackAutoFinder',
    ],
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'BUILD_ENVIRONMENT_FINDERS',
)


class ArtifactsSettings:
    """
    A settings object, that allows Artifacts settings to be accessed as
    properties.

    For example:

        from artifacts.settings import artifacts_settings
        print(artifacts_settings.BUILD_ENVIRONMENT_FINDERS)

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self._user_settings = user_settings if user_settings else {}
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'ARTIFACTS', {})
        return self._user_settings

    @functools.lru_cache(maxsize=None)
    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = import_string(val) if type(val) is not list else (
                [import_string(v) for v in val]
            )

        return val

    def reload(self):
        self.__getattr_.clear_cache()

        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


artifacts_settings = ArtifactsSettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_artifacts_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == 'ARTIFACTS':
        artifacts_settings.reload()


setting_changed.connect(reload_artifacts_settings)
