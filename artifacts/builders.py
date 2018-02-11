import json
import os
import subprocess


class WebpackBuilder:
    """
    """

    def __init__(self, working_dir, webpack, configuration, node):
        """
        """
        self.working_dir = working_dir
        self.webpack = webpack
        self.configuration = configuration
        self.node = node

    @property
    def _cmd(self):
        """
        """
        cmd = [self.node, self.webpack, '--json']

        if self.configuration:
            cmd += ['-c', self.configuration]
        else:
            cmd += [self.working_dir]

        return cmd

    @property
    def artifacts(self):
        """
        """
        json_output = json.loads(self._process.stdout)
        output_path = json_output['outputPath']

        for chunk in json_output['chunks']:
            for chunk_file in chunk['files']:
                yield os.path.join(output_path, chunk_file)

    def build(self):
        """
        """
        if not hasattr(self, '_process'):
            self._process = subprocess.run(
                self._cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_dir,
            )

        return bool(self._process.returncode)
