from django.apps import AppConfig


class FollowsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'follows'
    verbose_name = 'Follows'

    def ready(self):
        import follows.signals  # noqa
