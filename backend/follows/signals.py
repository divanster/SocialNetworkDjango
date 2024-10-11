# backend/follows/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Follow
from .tasks import send_follow_event_to_kafka
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Follow)
def follow_created(sender, instance, created, **kwargs):
    if created:
        # Trigger Celery task to send follow created event to Kafka
        send_follow_event_to_kafka.delay(instance.id, 'created')
        logger.info(f"Triggered Kafka task for follow created with ID {instance.id}")


@receiver(post_delete, sender=Follow)
def follow_deleted(sender, instance, **kwargs):
    # Trigger Celery task to send follow deleted event to Kafka
    send_follow_event_to_kafka.delay(instance.id, 'deleted')
    logger.info(f"Triggered Kafka task for follow deleted with ID {instance.id}")
