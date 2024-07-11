from django.apps import AppConfig

class LikesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'likes'
    verbose_name = 'Likes'

    # def ready(self):
    #     import likes.signals  # Import signals if you have any
