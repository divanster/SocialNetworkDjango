from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social'
    verbose_name = 'Social'

    def ready(self):
        """
        Import modules to ensure Django signals are registered.
        Celery tasks are managed within kafka_app.
        """
        # Removed the import since 'social.tasks' does not exist
        try:
            import social.signals  # Register signals
        except ImportError as e:
            raise ImportError(f"Error importing signals for app 'social': {e}")
