# backend/follows/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Follow
from .tasks import process_follow_event_task
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Follow)
def follow_created(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(
            lambda: process_follow_event_task.delay(instance.id, 'created'))
        logger.info(
            f"[SIGNAL] Triggered Celery task for follow created with ID {instance.id}")


@receiver(post_delete, sender=Follow)
def follow_deleted(sender, instance, **kwargs):
    transaction.on_commit(
        lambda: process_follow_event_task.delay(instance.id, 'deleted'))
    logger.info(
        f"[SIGNAL] Triggered Celery task for follow deleted with ID {instance.id}")
