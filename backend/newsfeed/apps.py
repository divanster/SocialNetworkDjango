from django.apps import AppConfig


class NewsfeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newsfeed'

    def ready(self):
        import newsfeed.signals # noqa
