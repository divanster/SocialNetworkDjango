from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Message
from kafka_app.tasks import process_message_event_task
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Message)
def message_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Trigger Celery task to process message event
    process_message_event_task.delay(instance.id, event_type)
    logger.info(f"Triggered Celery task for message {event_type} with ID {instance.id}")


@receiver(post_delete, sender=Message)
def message_deleted(sender, instance, **kwargs):
    # Trigger Celery task to process deleted message event
    process_message_event_task.delay(instance.id, 'deleted')
    logger.info(f"Triggered Celery task for deleted message with ID {instance.id}")
