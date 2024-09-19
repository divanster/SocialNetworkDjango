from django.apps import AppConfig


class MessengerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messenger'
    verbose_name = 'Messenger'

    # def ready(self):
    #     import messenger.signals  # Import signals if you have any
