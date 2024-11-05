# backend/albums/signals.py

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from albums.models import Album, Photo  # Import the updated Django models
from albums.tasks import process_album_event_task, process_photo_event_task
from core.choices import VisibilityChoices  # Import visibility choices

logger = logging.getLogger(__name__)


# Signals for the Album model

@receiver(post_save, sender=Album)
def album_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler for Album model. It triggers a Celery task when an album is created or updated,
    but only if the album is visible to either friends or public.

    Args:
        sender (Model): The model class (Album).
        instance (Album): The actual instance being saved.
        created (bool): A boolean indicating if the instance is being created.
        **kwargs: Additional keyword arguments.
    """
    # Respect the visibility setting
    if instance.visibility == VisibilityChoices.PRIVATE:
        logger.info(f"[SIGNAL] Album {instance.pk} is private. No task triggered.")
        return

    event_type = 'created' if created else 'updated'
    process_album_event_task.delay(str(instance.pk), event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for album {event_type} with ID {instance.pk}")


@receiver(post_delete, sender=Album)
def album_deleted(sender, instance, **kwargs):
    """
    Signal handler for Album model. It triggers a Celery task when an album is deleted,
    but only if the album was visible to either friends or public.

    Args:
        sender (Model): The model class (Album).
        instance (Album): The actual instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    # Respect the visibility setting
    if instance.visibility == VisibilityChoices.PRIVATE:
        logger.info(
            f"[SIGNAL] Album {instance.pk} was private. No task triggered for deletion.")
        return

    process_album_event_task.delay(str(instance.pk), 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for album deleted with ID {instance.pk}")


# Signals for the Photo model

@receiver(post_save, sender=Photo)
def photo_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler for Photo model. It triggers a Celery task when a photo is created or updated,
    but only if the associated album is visible to either friends or public.

    Args:
        sender (Model): The model class (Photo).
        instance (Photo): The actual instance being saved.
        created (bool): A boolean indicating if the instance is being created.
        **kwargs: Additional keyword arguments.
    """
    # Respect the visibility setting of the associated album
    if instance.album.visibility == VisibilityChoices.PRIVATE:
        logger.info(
            f"[SIGNAL] Photo {instance.pk} is part of a private album. No task triggered.")
        return

    event_type = 'created' if created else 'updated'
    process_photo_event_task.delay(str(instance.pk), event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for photo {event_type} with ID {instance.pk}")


@receiver(post_delete, sender=Photo)
def photo_deleted(sender, instance, **kwargs):
    """
    Signal handler for Photo model. It triggers a Celery task when a photo is deleted,
    but only if the associated album was visible to either friends or public.

    Args:
        sender (Model): The model class (Photo).
        instance (Photo): The actual instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    # Respect the visibility setting of the associated album
    if instance.album.visibility == VisibilityChoices.PRIVATE:
        logger.info(
            f"[SIGNAL] Photo {instance.pk} was part of a private album. No task triggered for deletion.")
        return

    process_photo_event_task.delay(str(instance.pk), 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for photo deleted with ID {instance.pk}")


@receiver(post_delete, sender=Album)
def cascade_delete_photos(sender, instance, **kwargs):
    # Soft delete all related photos when an album is deleted
    instance.photos.update(is_deleted=True)
