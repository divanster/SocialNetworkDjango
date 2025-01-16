# backend/notifications/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from kafka_app.tasks.notification_tasks import process_notification_event_task  # Updated import
import logging

from kafka_app.constants import (
    NOTIFICATION_CREATED,
    NOTIFICATION_UPDATED,
    NOTIFICATION_DELETED,
    NOTIFICATIONS
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def notification_saved(sender, instance, created, **kwargs):
    """
    Signal to handle notification creation and updates.
    Triggers a Celery task to process the event.
    """
    if instance.is_deleted:
        # If the notification is soft-deleted via save(), treat it as a 'deleted' event
        event_type = NOTIFICATION_DELETED
    else:
        event_type = NOTIFICATION_CREATED if created else 'updated'  # Consider defining NOTIFICATION_UPDATED

    # Trigger Celery task to process notification event
    try:
        process_notification_event_task.delay(str(instance.id), event_type)
        logger.debug(
            f"Triggered Celery task for notification {event_type} event with ID {instance.id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to trigger Celery task for notification {event_type} event with ID {instance.id}: {e}"
        )


@receiver(post_delete, sender=Notification)
def notification_deleted(sender, instance, **kwargs):
    """
    Signal to handle notification deletion.
    Triggers a Celery task to process the 'deleted' event.
    """
    # Trigger Celery task to process deleted notification event
    try:
        process_notification_event_task.delay(str(instance.id), NOTIFICATION_DELETED)
        logger.debug(
            f"Triggered Celery task for notification deleted event with ID {instance.id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to trigger Celery task for notification deleted event with ID {instance.id}: {e}"
        )
