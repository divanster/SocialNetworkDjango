# backend/messenger/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Message
from kafka_app.tasks.messenger_tasks import process_message_event_task
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from kafka_app.constants import (
    MESSAGE_CREATED,
    MESSAGE_UPDATED,
    MESSAGE_DELETED,
    MESSENGER_EVENTS
)
from .serializers import MessageSerializer

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

    if created:
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"messenger_{instance.receiver_id}",
                {
                    "type": "messenger_event",
                    "payload": MessageSerializer(instance).data,
                }
            )
        except Exception as exc:
            logger.warning("Failed to send realtime messenger event: %s", exc)


@receiver(post_delete, sender=Message)
def message_deleted(sender, instance, **kwargs):
    """
    Signal to handle message deletion.
    Triggers a Celery task to process the 'deleted' event.
    """
    # Trigger Celery task to process deleted message event
    process_message_event_task.delay(str(instance.id), MESSAGE_DELETED)
    logger.info(f"Triggered Celery task for deleted message with ID {instance.id}")
