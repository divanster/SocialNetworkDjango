# backend/friends/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FriendRequest, Friendship
from kafka_app.tasks.friend_tasks import process_friend_event_task  # Updated import
import logging

from kafka_app.constants import (
    FRIEND_ADDED,
    FRIEND_REMOVED,
    FRIEND_EVENTS
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=FriendRequest)
def friend_request_saved(sender, instance, created, **kwargs):
    """
    Signal handler for saving FriendRequest instances.
    Triggers a Celery task for creation or update events.
    """
    if not instance.is_deleted:
        # Determine the type of event: creation or update
        event_type = 'created' if created else 'updated'  # Consider defining FRIEND_REQUEST_CREATED, etc.

        # Trigger Celery task to process the friend request event
        process_friend_event_task.delay(str(instance.id), event_type, is_friendship=False)
        logger.info(
            f"Triggered Celery task for friend request {event_type} with ID {instance.id}"
        )


@receiver(post_delete, sender=FriendRequest)
def friend_request_deleted(sender, instance, **kwargs):
    """
    Signal handler for deleting FriendRequest instances.
    Triggers a Celery task for deletion events.
    """
    if not instance.is_deleted:
        # Trigger Celery task to process the friend request deleted event
        process_friend_event_task.delay(str(instance.id), 'deleted', is_friendship=False)
        logger.info(
            f"Triggered Celery task for deleted friend request with ID {instance.id}"
        )


@receiver(post_save, sender=Friendship)
def friendship_saved(sender, instance, created, **kwargs):
    """
    Signal handler for saving Friendship instances.
    Triggers a Celery task for creation or update events.
    """
    if not instance.is_deleted:
        if created:
            # Trigger Celery task to process the friendship created event
            process_friend_event_task.delay(str(instance.id), FRIEND_ADDED, is_friendship=True)
            logger.info(
                f"Triggered Celery task for friendship created with ID {instance.id}"
            )
        else:
            # Handle updates if necessary
            process_friend_event_task.delay(str(instance.id), 'updated', is_friendship=True)
            logger.info(
                f"Triggered Celery task for friendship updated with ID {instance.id}"
            )


@receiver(post_delete, sender=Friendship)
def friendship_deleted(sender, instance, **kwargs):
    """
    Signal handler for deleting Friendship instances.
    Triggers a Celery task for deletion events.
    """
    if not instance.is_deleted:
        # Trigger Celery task to process the friendship deleted event
        process_friend_event_task.delay(str(instance.id), FRIEND_REMOVED, is_friendship=True)
        logger.info(
            f"Triggered Celery task for deleted friendship with ID {instance.id}"
        )
