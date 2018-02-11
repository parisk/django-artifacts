from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
import delegator


WEBPACK_DIRS = [
    'web',
]


class ArtifactsStorage(ManifestStaticFilesStorage):
    def post_process(self, paths, **options):
        for path in WEBPACK_DIRS:
            webpack_dir_path = self.path(path)
            webpack_bin_path = f'{webpack_dir_path}/node_modules/webpack/bin/webpack.js'
            print(f'Running webpack in "{webpack_dir_path}"')
            w = delegator.run(
                ['node', webpack_bin_path, '.'], cwd=webpack_dir_path,
            )
            import pdb
            pdb.set_trace()
            print(w.return_code)
            print(w.out)
            print(w.err)

        # return super().post_process(paths, **options)
        return []
