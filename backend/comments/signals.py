# backend/comments/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment
from comments.tasks import send_comment_event_to_kafka


@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    """
    Signal handler for creating or updating comments.
    Triggers Celery task to send Kafka message.
    """
    event_type = 'created' if created else 'updated'
    send_comment_event_to_kafka.delay(instance.id, event_type)


@receiver(post_delete, sender=Comment)
def comment_deleted(sender, instance, **kwargs):
    """
    Signal handler for deleting comments.
    Triggers Celery task to send Kafka message.
    """
    send_comment_event_to_kafka.delay(instance.id, 'deleted')
