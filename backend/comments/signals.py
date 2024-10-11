# backend/comments/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment
from .tasks import send_comment_event_to_kafka
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def comment_created_or_updated(sender, instance, created, **kwargs):
    if created:
        # Trigger Celery task to send comment created event to Kafka
        send_comment_event_to_kafka.delay(instance.id, 'created')
        logger.info(f"Triggered Kafka task for comment created with ID {instance.id}")
    else:
        # Trigger Celery task to send comment updated event to Kafka
        send_comment_event_to_kafka.delay(instance.id, 'updated')
        logger.info(f"Triggered Kafka task for comment updated with ID {instance.id}")


@receiver(post_delete, sender=Comment)
def comment_deleted(sender, instance, **kwargs):
    # Trigger Celery task to send comment deleted event to Kafka
    send_comment_event_to_kafka.delay(instance.id, 'deleted')
    logger.info(f"Triggered Kafka task for comment deleted with ID {instance.id}")
