# backend/pages/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Page
from .tasks import send_page_event_to_kafka  # Import the Celery task
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Page)
def page_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Trigger the Celery task to send the page event to Kafka
    send_page_event_to_kafka.delay(instance.id, event_type)
    logger.info(
        f"Triggered Celery task for page {event_type} event with ID {instance.id}")


@receiver(post_delete, sender=Page)
def page_deleted(sender, instance, **kwargs):
    # Trigger the Celery task to send the page deletion event to Kafka
    send_page_event_to_kafka.delay(instance.id, 'deleted')
    logger.info(f"Triggered Celery task for page deleted event with ID {instance.id}")
