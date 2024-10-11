# backend/newsfeed/signals.py

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from stories.models import Story
from .tasks import send_newsfeed_event_to_kafka

logger = logging.getLogger(__name__)

# A list of models to apply the signal handlers
NEWSFEED_MODELS = [Post, Comment, Reaction, Album, Story]

# General save signal handler for all models
for model in NEWSFEED_MODELS:
    @receiver(post_save, sender=model)
    def handle_model_save(sender, instance, created, **kwargs):
        event_type = 'created' if created else 'updated'

        # Use Celery to send Kafka message
        send_newsfeed_event_to_kafka.delay(instance.id, event_type, sender.__name__)
        logger.info(
            f"Newsfeed: {event_type} event sent for {sender.__name__} with ID {instance.id}")


    @receiver(post_delete, sender=model)
    def handle_model_delete(sender, instance, **kwargs):
        # Use Celery to send Kafka message for deletion
        send_newsfeed_event_to_kafka.delay(instance.id, 'deleted', sender.__name__)
        logger.info(
            f"Newsfeed: deleted event sent for {sender.__name__} with ID {instance.id}")
