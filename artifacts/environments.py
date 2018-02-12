import json
import os
import subprocess

from .settings import artifacts_settings


class BuildEnvironment:
    """
    """

    def __init__(self, storage, path, options={}):
        self.storage = storage
        self.path = path
        self.options = options


class WebpackBuildEnvironment(BuildEnvironment):
    """
    """

    @property
    def webpack_bin(self):
        default_webpack_bin = 'node_modules/webpack/bin/webpack.js'
        return self.options.get('webpack_bin', default_webpack_bin)

    @property
    def webpack_config(self):
        config_file = 'webpack.config.js'
        default_webpack_config = config_file if (
            self.storage.exists(config_file)
        ) else None
        return self.options.get('webpack_config', default_webpack_config)

    @property
    def node_path(self):
        return self.options.get('node_path', artifacts_settings.NODE_PATH)

    @property
    def label(self):
        return f'[webpack build environment in {self.path}]'

    @property
    def webpack_root(self):
        """
        """
        return self.storage.path(self.path)

    @property
    def _cmd(self):
        """
        """
        cmd = [self.node_path, self.webpack_bin, '--json']
        cmd += ['-c', self.webpack_config] if self.webpack_config else ['.']

        return cmd

    @property
    def artifacts(self):
        """
        """
        json_output = json.loads(self._process.stdout)
        output_path = json_output['outputPath']

        if output_path.startswith(f'{self.webpack_root}/'):
            output_path = output_path[len(f'{self.webpack_root}/'):]
            output_path = os.path.join(self.path, output_path)

        for chunk in json_output['chunks']:
            yield from [
                os.path.join(output_path, _file) for _file in chunk['files']
            ]

    def build(self):
        """
        """
        if not hasattr(self, '_process'):
            self._process = subprocess.run(
                self._cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.webpack_root,
            )

        return bool(self._process.returncode)

    def build_artifacts(self):
        """
        """
        self.build()
        yield from self.artifacts
