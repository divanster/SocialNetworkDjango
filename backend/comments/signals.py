# backend/comments/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment
from kafka_app.tasks import process_comment_event_task
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def comment_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal to handle comment creation or update.
    Triggers a Celery task to process the comment event.

    Args:
        sender (Model class): The model class that sent the signal.
        instance (Comment): The actual instance being saved.
        created (bool): Boolean; True if a new record was created.
    """
    event_type = 'created' if created else 'updated'
    # Trigger the Celery task for processing the event asynchronously
    process_comment_event_task.delay(instance.id, event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for comment {event_type} with ID {instance.id}")


@receiver(post_delete, sender=Comment)
def comment_deleted(sender, instance, **kwargs):
    """
    Signal to handle comment deletion.
    Triggers a Celery task to process the deletion event.

    Args:
        sender (Model class): The model class that sent the signal.
        instance (Comment): The actual instance being deleted.
    """
    # Trigger the Celery task for processing the deletion event asynchronously
    process_comment_event_task.delay(instance.id, 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for comment deleted with ID {instance.id}")
