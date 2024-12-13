from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social'
    verbose_name = 'Social'

    def ready(self):
        import social.tasks  # Ensure Celery tasks are registered
        import social.signals  # Ensure signals are registered (if applicable)
