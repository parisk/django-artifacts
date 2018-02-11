from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ArtifactsStorage(ManifestStaticFilesStorage):
    def post_process(self, *args, **kwargs):
        pass
