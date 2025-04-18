# tagging/apps.py

from django.apps import AppConfig


class TaggingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tagging'

    def ready(self):
        import tagging.signals  # noqa
