# backend/messenger/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Message
from kafka_app.tasks.messenger_tasks import process_message_event_task
import logging

from kafka_app.constants import (
    MESSAGE_CREATED,
    MESSAGE_UPDATED,
    MESSAGE_DELETED,
    MESSENGER_EVENTS
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Message)
def message_saved(sender, instance, created, **kwargs):
    """
    Signal to handle message creation and updates.
    Triggers a Celery task to process the event.
    """
    if instance.is_deleted:
        # If the message is soft-deleted via save(), treat it as a 'deleted' event
        event_type = MESSAGE_DELETED
    else:
        event_type = MESSAGE_CREATED if created else MESSAGE_UPDATED

    # Trigger Celery task to process message event
    process_message_event_task.delay(str(instance.id), event_type)
    logger.info(f"Triggered Celery task for message {event_type} with ID {instance.id}")


@receiver(post_delete, sender=Message)
def message_deleted(sender, instance, **kwargs):
    """
    Signal to handle message deletion.
    Triggers a Celery task to process the 'deleted' event.
    """
    # Trigger Celery task to process deleted message event
    process_message_event_task.delay(str(instance.id), MESSAGE_DELETED)
    logger.info(f"Triggered Celery task for deleted message with ID {instance.id}")
