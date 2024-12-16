from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social'
    verbose_name = 'Social'

    def ready(self):
        """
        Import modules to ensure Celery tasks and Django signals are registered.
        These imports are critical for tasks and signals to function as expected.
        """
        try:
            import social.tasks  # Register Celery tasks
        except ImportError as e:
            raise ImportError(f"Error importing tasks for app 'social': {e}")

        try:
            import social.signals  # Register signals
        except ImportError as e:
            raise ImportError(f"Error importing signals for app 'social': {e}")
