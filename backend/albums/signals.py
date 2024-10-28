# backend/albums/signals.py

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from albums.models import Album, Photo  # Import the updated Django models
from albums.tasks import process_album_event_task, process_photo_event_task

logger = logging.getLogger(__name__)


# Signals for the Album model


@receiver(post_save, sender=Album)
def album_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler for Album model. It triggers a Celery task when an album is created or updated.

    Args:
        sender (Model): The model class (Album).
        instance (Album): The actual instance being saved.
        created (bool): A boolean indicating if the instance is being created.
        **kwargs: Additional keyword arguments.
    """
    event_type = 'created' if created else 'updated'
    process_album_event_task.delay(str(instance.pk), event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for album {event_type} with ID {instance.pk}")


@receiver(post_delete, sender=Album)
def album_deleted(sender, instance, **kwargs):
    """
    Signal handler for Album model. It triggers a Celery task when an album is deleted.

    Args:
        sender (Model): The model class (Album).
        instance (Album): The actual instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    process_album_event_task.delay(str(instance.pk), 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for album deleted with ID {instance.pk}")


# Signals for the Photo model


@receiver(post_save, sender=Photo)
def photo_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler for Photo model. It triggers a Celery task when a photo is created or updated.

    Args:
        sender (Model): The model class (Photo).
        instance (Photo): The actual instance being saved.
        created (bool): A boolean indicating if the instance is being created.
        **kwargs: Additional keyword arguments.
    """
    event_type = 'created' if created else 'updated'
    process_photo_event_task.delay(str(instance.pk), event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for photo {event_type} with ID {instance.pk}")


@receiver(post_delete, sender=Photo)
def photo_deleted(sender, instance, **kwargs):
    """
    Signal handler for Photo model. It triggers a Celery task when a photo is deleted.

    Args:
        sender (Model): The model class (Photo).
        instance (Photo): The actual instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    process_photo_event_task.delay(str(instance.pk), 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for photo deleted with ID {instance.pk}")
