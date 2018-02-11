import json
import os
import subprocess


class WebpackBuilder:
    """
    """

    def __init__(self, working_dir, webpack=None, configuration=None):
        """
        """
        self.working_dir = working_dir
        self.webpack = webpack or os.path.join(
            self.working_dir, 'node_modules/webpack/bin/webpack.js',
        )

        _configuration = configuration

        if _configuration:
            _configuration = os.path.join(
                _configuration, 'node_modules/webpack/bin/webpack.js',
            )

        self.configuration = _configuration

    @property
    def cmd(self):
        """
        """
        args = ['node', self.webpack, '--json']

        if self.configuration:
            args += ['-c', self.configuration]
        else:
            args += [self.working_dir]

        return args

    @property
    def artifacts(self):
        """
        """
        json_output = json.loads(self._process.stdout)
        output_path = json_output['outputPath']

        for chunk in json_output['chunks']:
            for chunk_file in chunk['files']:
                yield os.path.join(output_path, chunk_file)

    def run(self):
        """
        """
        if not hasattr(self, '_process'):
            self._process = subprocess.run(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_dir,
            )

        return bool(self._process.returncode)
