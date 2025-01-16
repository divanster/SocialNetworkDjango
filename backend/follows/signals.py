# backend/follows/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from follows.models import Follow
from kafka_app.tasks.follow_tasks import process_follow_event_task  # Updated import
import logging

from kafka_app.constants import (
    FOLLOW_CREATED,
    FOLLOW_DELETED,
    FOLLOW_EVENTS
)

logger = logging.getLogger(__name__)


# Signal for Follow model when a follow is created or updated
@receiver(post_save, sender=Follow)
def follow_saved(sender, instance, created, **kwargs):
    try:
        # Define the event type based on the follow state
        event_type = FOLLOW_CREATED if created else 'follow_updated'  # Consider defining FOLLOW_UPDATED

        # Trigger the Celery task to send the event to Kafka
        process_follow_event_task.delay(str(instance.id), event_type)
        logger.info(f"Triggered follow event for Follow ID {instance.id}, Event Type {event_type}")

    except Exception as e:
        logger.error(f"Error handling follow event for Follow ID {instance.id}: {e}")


# Signal for Follow model when a follow is deleted
@receiver(post_delete, sender=Follow)
def follow_deleted(sender, instance, **kwargs):
    try:
        # Define the event type for deleted follow
        event_type = FOLLOW_DELETED

        # Trigger the Celery task to send the deleted event to Kafka
        process_follow_event_task.delay(str(instance.id), event_type)
        logger.info(f"Triggered follow deleted event for Follow ID {instance.id}")

    except Exception as e:
        logger.error(f"Error handling follow deletion for Follow ID {instance.id}: {e}")
