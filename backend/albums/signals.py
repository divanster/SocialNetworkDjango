# backend/albums/signals.py

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from albums.models import Album, Photo  # Import the updated Django models
from kafka_app.tasks.album_tasks import process_album_event_task, process_photo_event_task  # Correct import path
from core.choices import VisibilityChoices  # Import visibility choices
from core.signals import soft_delete, restore  # Import custom signals

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from utils.group_names import get_user_group_name  # Import utility function

logger = logging.getLogger(__name__)


# ===========================
# Album Signals
# ===========================

@receiver(post_save, sender=Album)
def album_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler for Album model. It triggers a Celery task when an album is created or updated,
    and sends relevant event details to Kafka and WebSocket groups based on visibility.

    Args:
        sender (Model): The model class (Album).
        instance (Album): The actual instance being saved.
        created (bool): A boolean indicating if the instance is being created.
        **kwargs: Additional keyword arguments.
    """
    event_type = 'created' if created else 'updated'

    try:
        # Respect the visibility setting
        if instance.visibility == VisibilityChoices.PRIVATE:
            logger.info(f"[SIGNAL] Album {instance.pk} is private. No task triggered.")
            return

        # Trigger Celery task for album creation or update
        process_album_event_task.delay(str(instance.pk), event_type)
        logger.info(
            f"[SIGNAL] Triggered Celery task for album {event_type} with ID {instance.pk}")

        # Send WebSocket notification
        user_group_name = get_user_group_name(
            instance.user.id)  # Assuming Album has a user field
        channel_layer = get_channel_layer()
        message = f"Your album '{instance.title}' has been {event_type}."
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'album_notification',
                'message': message,
                'event': event_type,
                'album_id': str(instance.id),
                'user_id': str(instance.user.id),
                'username': instance.user.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for album {event_type} with ID {instance.pk}")

    except Exception as e:
        logger.error(f"Error in album_created_or_updated signal: {e}")


@receiver(soft_delete, sender=Album)
def album_soft_deleted(sender, instance, **kwargs):
    """
    Custom signal handler to process soft deletion of Album.
    Triggers a Celery task and sends a WebSocket notification.

    Args:
        sender (Model): The model class (Album).
        instance (Album): The instance being soft-deleted.
        **kwargs: Additional keyword arguments.
    """
    try:
        # Trigger Celery task to handle the album soft deletion event
        process_album_event_task.delay(str(instance.pk), 'soft_deleted')
        logger.info(
            f"[SIGNAL] Triggered Celery task for album soft deletion with ID {instance.pk}")

        # Send WebSocket notification for album soft deletion
        user_group_name = get_user_group_name(
            instance.user.id)  # Assuming Album has a user field
        channel_layer = get_channel_layer()
        message = f"Your album '{instance.title}' has been soft-deleted."
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'album_notification',
                'message': message,
                'event': 'soft_deleted',
                'album_id': str(instance.id),
                'user_id': str(instance.user.id),
                'username': instance.user.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for album soft deletion with ID {instance.pk}")

    except Exception as e:
        logger.error(f"Error in album_soft_deleted signal: {e}")


@receiver(restore, sender=Album)
def album_restored(sender, instance, **kwargs):
    """
    Custom signal handler to process restoration of a soft-deleted Album.
    Triggers a Celery task and sends a WebSocket notification.

    Args:
        sender (Model): The model class (Album).
        instance (Album): The instance being restored.
        **kwargs: Additional keyword arguments.
    """
    try:
        # Trigger Celery task to handle the album restoration event
        process_album_event_task.delay(str(instance.pk), 'restored')
        logger.info(
            f"[SIGNAL] Triggered Celery task for album restoration with ID {instance.pk}")

        # Send WebSocket notification for album restoration
        user_group_name = get_user_group_name(
            instance.user.id)  # Assuming Album has a user field
        channel_layer = get_channel_layer()
        message = f"Your album '{instance.title}' has been restored."
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'album_notification',
                'message': message,
                'event': 'restored',
                'album_id': str(instance.id),
                'user_id': str(instance.user.id),
                'username': instance.user.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for album restoration with ID {instance.pk}")

    except Exception as e:
        logger.error(f"Error in album_restored signal: {e}")


# ===========================
# Photo Signals
# ===========================

@receiver(post_save, sender=Photo)
def photo_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler for Photo model. It triggers a Celery task when a photo is created or updated,
    and sends relevant event details to Kafka and WebSocket groups based on the album's visibility.

    Args:
        sender (Model): The model class (Photo).
        instance (Photo): The actual instance being saved.
        created (bool): A boolean indicating if the instance is being created.
        **kwargs: Additional keyword arguments.
    """
    event_type = 'created' if created else 'updated'

    try:
        # Respect the visibility setting of the associated album
        if instance.album.visibility == VisibilityChoices.PRIVATE:
            logger.info(
                f"[SIGNAL] Photo {instance.pk} is part of a private album. No task triggered.")
            return

        # Trigger Celery task for photo creation or update
        process_photo_event_task.delay(str(instance.pk), event_type)
        logger.info(
            f"[SIGNAL] Triggered Celery task for photo {event_type} with ID {instance.pk}")

        # Send WebSocket notification
        user_group_name = get_user_group_name(
            instance.album.user.id)  # Assuming Photo has album and Album has user
        channel_layer = get_channel_layer()
        message = f"Your photo has been {event_type} in album '{instance.album.title}'."
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'photo_notification',
                'message': message,
                'event': event_type,
                'photo_id': str(instance.id),
                'album_id': str(instance.album.id),
                'user_id': str(instance.album.user.id),
                'username': instance.album.user.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for photo {event_type} with ID {instance.pk}")

    except Exception as e:
        logger.error(f"Error in photo_created_or_updated signal: {e}")


@receiver(soft_delete, sender=Photo)
def photo_soft_deleted(sender, instance, **kwargs):
    """
    Custom signal handler to process soft deletion of Photo.
    Triggers a Celery task and sends a WebSocket notification.

    Args:
        sender (Model): The model class (Photo).
        instance (Photo): The instance being soft-deleted.
        **kwargs: Additional keyword arguments.
    """
    try:
        # Trigger Celery task to handle the photo soft deletion event
        process_photo_event_task.delay(str(instance.pk), 'soft_deleted')
        logger.info(
            f"[SIGNAL] Triggered Celery task for photo soft deletion with ID {instance.pk}")

        # Send WebSocket notification for photo soft deletion
        user_group_name = get_user_group_name(
            instance.album.user.id)  # Assuming Photo has album and Album has user
        channel_layer = get_channel_layer()
        message = f"Your photo in album '{instance.album.title}' has been soft-deleted."
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'photo_notification',
                'message': message,
                'event': 'soft_deleted',
                'photo_id': str(instance.id),
                'album_id': str(instance.album.id),
                'user_id': str(instance.album.user.id),
                'username': instance.album.user.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for photo soft deletion with ID {instance.pk}")

    except Exception as e:
        logger.error(f"Error in photo_soft_deleted signal: {e}")


@receiver(restore, sender=Photo)
def photo_restored(sender, instance, **kwargs):
    """
    Custom signal handler to process restoration of a soft-deleted Photo.
    Triggers a Celery task and sends a WebSocket notification.

    Args:
        sender (Model): The model class (Photo).
        instance (Photo): The instance being restored.
        **kwargs: Additional keyword arguments.
    """
    try:
        # Trigger Celery task to handle the photo restoration event
        process_photo_event_task.delay(str(instance.pk), 'restored')
        logger.info(
            f"[SIGNAL] Triggered Celery task for photo restoration with ID {instance.pk}")

        # Send WebSocket notification for photo restoration
        user_group_name = get_user_group_name(
            instance.album.user.id)  # Assuming Photo has album and Album has user
        channel_layer = get_channel_layer()
        message = f"Your photo in album '{instance.album.title}' has been restored."
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'photo_notification',
                'message': message,
                'event': 'restored',
                'photo_id': str(instance.id),
                'album_id': str(instance.album.id),
                'user_id': str(instance.album.user.id),
                'username': instance.album.user.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for photo restoration with ID {instance.pk}")

    except Exception as e:
        logger.error(f"Error in photo_restored signal: {e}")
