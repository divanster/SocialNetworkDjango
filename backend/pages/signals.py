# backend/pages/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Page
from .tasks import send_page_event_to_kafka  # Import the Celery task
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Page)
def page_saved(sender, instance, created, **kwargs):
    """
    Signal handler that triggers when a Page instance is created or updated.
    Sends an event to Kafka through a Celery task.
    """
    event_type = 'created' if created else 'updated'

    try:
        # Trigger the Celery task to send the page event to Kafka
        send_page_event_to_kafka.delay(instance.id, event_type)
        logger.info(
            f"[SIGNAL] Triggered Celery task for page {event_type} event with ID {instance.id} and title '{instance.title}'"
        )
    except Exception as e:
        logger.error(
            f"[SIGNAL] Failed to trigger Celery task for page {event_type} event with ID {instance.id} and title '{instance.title}': {e}"
        )


@receiver(post_delete, sender=Page)
def page_deleted(sender, instance, **kwargs):
    """
    Signal handler that triggers when a Page instance is deleted.
    Sends a delete event to Kafka through a Celery task.
    """
    try:
        # Trigger the Celery task to send the page deletion event to Kafka
        send_page_event_to_kafka.delay(instance.id, 'deleted')
        logger.info(
            f"[SIGNAL] Triggered Celery task for page deleted event with ID {instance.id} and title '{instance.title}'"
        )
    except Exception as e:
        logger.error(
            f"[SIGNAL] Failed to trigger Celery task for page deleted event with ID {instance.id} and title '{instance.title}': {e}"
        )
