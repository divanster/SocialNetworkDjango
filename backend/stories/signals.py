# backend/stories/signals.py

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Story
from .tasks import send_story_event_to_kafka  # Import task to send event to Kafka

# Initialize logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Story)
def story_saved(sender, instance, created, **kwargs):
    """
    Signal to handle logic after a Story instance is saved.
    Logs whether the story was created or updated and sends an event to Kafka.
    """
    event_type = 'created' if created else 'updated'
    logger.info(f'Story {event_type} with ID: {instance.id}, User: {instance.user_username}, Content: {instance.content[:30]}')

    # Send story event to Kafka
    send_story_event_to_kafka.delay(instance.id, event_type)


@receiver(post_delete, sender=Story)
def story_deleted(sender, instance, **kwargs):
    """
    Signal to handle logic after a Story instance is deleted.
    Logs the deletion of the story and sends an event to Kafka.
    """
    logger.info(f'Story deleted with ID: {instance.id}, User: {instance.user_username}, Content: {instance.content[:30]}')

    # Send story event to Kafka
    send_story_event_to_kafka.delay(instance.id, 'deleted')
