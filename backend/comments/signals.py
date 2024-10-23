# backend/comments/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment
from .tasks import process_comment_event_task
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def comment_created_or_updated(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    process_comment_event_task.delay(instance.id, event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for comment {event_type} with ID {instance.id}")


@receiver(post_delete, sender=Comment)
def comment_deleted(sender, instance, **kwargs):
    process_comment_event_task.delay(instance.id, 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for comment deleted with ID {instance.id}")
