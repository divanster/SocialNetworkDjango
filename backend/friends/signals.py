from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FriendRequest, Friendship
from .tasks import process_friend_event
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=FriendRequest)
def friend_request_saved(sender, instance, created, **kwargs):
    # Determine the type of event: creation or update
    event_type = 'created' if created else 'updated'

    # Trigger Celery task to process the friend request event
    process_friend_event.delay(instance.id, event_type, is_friendship=False)
    logger.info(
        f"Triggered Celery task for friend request {event_type} with ID {instance.id}"
    )


@receiver(post_delete, sender=FriendRequest)
def friend_request_deleted(sender, instance, **kwargs):
    # Trigger Celery task to process the friend request deleted event
    process_friend_event.delay(instance.id, 'deleted', is_friendship=False)
    logger.info(
        f"Triggered Celery task for deleted friend request with ID {instance.id}"
    )


@receiver(post_save, sender=Friendship)
def friendship_saved(sender, instance, created, **kwargs):
    if created:
        # Trigger Celery task to process the friendship created event
        process_friend_event.delay(instance.id, 'created', is_friendship=True)
        logger.info(
            f"Triggered Celery task for friendship created with ID {instance.id}"
        )


@receiver(post_delete, sender=Friendship)
def friendship_deleted(sender, instance, **kwargs):
    # Trigger Celery task to process the friendship deleted event
    process_friend_event.delay(instance.id, 'deleted', is_friendship=True)
    logger.info(
        f"Triggered Celery task for deleted friendship with ID {instance.id}"
    )
