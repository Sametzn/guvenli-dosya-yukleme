from django.apps import AppConfig

class UploadConfig(AppConfig):
    name = 'upload'

    def ready(self):
        import upload.signals