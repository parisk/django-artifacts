import json
import os
import subprocess


class WebpackBuilder:
    """
    """

    def __init__(self, storage, webpack_root, webpack_bin, webpack_config, node_path):
        """
        """
        self._storage = storage
        self._webpack_root = webpack_root
        self.webpack_bin = webpack_bin
        self.webpack_config = webpack_config
        self.node_path = node_path

    @property
    def webpack_root(self):
        """
        """
        return self._storage.path(self._webpack_root)

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
            output_path = os.path.join(self._webpack_root, output_path)

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
                cwd=self.webpack_root,
            )

        return bool(self._process.returncode)
