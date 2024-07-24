from django.apps import AppConfig


class ReactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reactions'
    verbose_name = 'Reactions'

    # def ready(self):
    #     import reactions.signals  # Import signals if you have any
