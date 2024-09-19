# backend/albums/apps.py

from django.apps import AppConfig


class AlbumsConfig(AppConfig):
    name = 'albums'

    def ready(self):
        import albums.signals
