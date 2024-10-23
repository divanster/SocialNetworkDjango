# backend/albums/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Album, Photo
from .tasks import process_album_event_task, process_photo_event_task
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Album)
def album_created_or_updated(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    process_album_event_task.delay(instance.id, event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for album {event_type} with ID {instance.id}")


@receiver(post_delete, sender=Album)
def album_deleted(sender, instance, **kwargs):
    process_album_event_task.delay(instance.id, 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for album deleted with ID {instance.id}")


@receiver(post_save, sender=Photo)
def photo_created_or_updated(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    process_photo_event_task.delay(instance.id, event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for photo {event_type} with ID {instance.id}")


@receiver(post_delete, sender=Photo)
def photo_deleted(sender, instance, **kwargs):
    process_photo_event_task.delay(instance.id, 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for photo deleted with ID {instance.id}")
