from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from .tasks import process_notification_event_task  # Import the Celery task
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def notification_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Trigger the Celery task to process the notification event
    try:
        process_notification_event_task.delay(instance.id, event_type)
        logger.debug(
            f"Triggered Celery task for notification {event_type} event with ID {instance.id}")
    except Exception as e:
        logger.error(
            f"Failed to trigger Celery task for notification {event_type} event with ID {instance.id}: {e}")


@receiver(post_delete, sender=Notification)
def notification_deleted(sender, instance, **kwargs):
    # Trigger the Celery task to process the notification deletion
    try:
        process_notification_event_task.delay(instance.id, 'deleted')
        logger.debug(
            f"Triggered Celery task for notification deleted event with ID {instance.id}")
    except Exception as e:
        logger.error(
            f"Failed to trigger Celery task for notification deleted event with ID {instance.id}: {e}")
