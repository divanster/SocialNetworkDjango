# backend/friends/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FriendRequest, Friendship
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
import logging

from .tasks import send_email_friend_request


# Initialize logging
logger = logging.getLogger(__name__)


# Helper function to send real-time notifications
def send_real_time_notification(user_id, message, notification_type):
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'friend_requests_{user_id}',
            {
                'type': notification_type,
                'message': message
            }
        )
    except Exception as e:
        logger.error(f"Error sending real-time notification: {e}")


# Signal handler for FriendRequest creation and updates
@receiver(post_save, sender=FriendRequest)
def friend_request_saved(sender, instance, created, **kwargs):
    try:
        if created:
            # Notify the receiver in real-time
            send_real_time_notification(
                instance.receiver.id,
                f"You have a new friend request from {instance.sender.username}.",
                'friend_request_notification'
            )
            logger.info(f'FriendRequest created: {instance}')

            # Send email notification to the receiver asynchronously using Celery
            send_email_friend_request.delay(instance.sender.username,
                                            instance.receiver.email)

        # Automatically create a friendship if the friend request is accepted
        if instance.status == 'accepted':
            friendship, created = Friendship.objects.get_or_create(
                user1=min(instance.sender, instance.receiver, key=lambda u: u.id),
                user2=max(instance.sender, instance.receiver, key=lambda u: u.id),
            )
            if created:
                logger.info(
                    f'Friendship created automatically after friend request acceptance: {friendship}')
    except ValidationError as e:
        logger.error(f'Error creating friendship: {e}')
    except Exception as ex:
        logger.error(f"Unexpected error in friend_request_saved: {ex}")


# Signal handler for FriendRequest deletion
@receiver(post_delete, sender=FriendRequest)
def friend_request_deleted(sender, instance, **kwargs):
    try:
        # Notify both the sender and receiver in real-time that the friend request was deleted
        send_real_time_notification(
            instance.receiver.id,
            f"Friend request from {instance.sender.username} has been deleted.",
            'friend_request_notification'
        )
        send_real_time_notification(
            instance.sender.id,
            f"Your friend request to {instance.receiver.username} has been deleted.",
            'friend_request_notification'
        )
        logger.info(f'FriendRequest deleted: {instance}')
    except Exception as e:
        logger.error(f"Error deleting FriendRequest: {e}")


# Signal handler for Friendship creation
@receiver(post_save, sender=Friendship)
def friendship_saved(sender, instance, created, **kwargs):
    if created:
        try:
            # Notify both users in real-time that the friendship was created
            send_real_time_notification(
                instance.user1.id,
                f"You are now friends with {instance.user2.username}.",
                'friendship_notification'
            )
            send_real_time_notification(
                instance.user2.id,
                f"You are now friends with {instance.user1.username}.",
                'friendship_notification'
            )
            logger.info(f'Friendship created: {instance}')
        except Exception as e:
            logger.error(f"Error creating Friendship: {e}")


# Signal handler for Friendship deletion
@receiver(post_delete, sender=Friendship)
def friendship_deleted(sender, instance, **kwargs):
    try:
        # Notify both users in real-time that the friendship was deleted
        send_real_time_notification(
            instance.user1.id,
            f"Your friendship with {instance.user2.username} has been removed.",
            'friendship_notification'
        )
        send_real_time_notification(
            instance.user2.id,
            f"Your friendship with {instance.user1.username} has been removed.",
            'friendship_notification'
        )
        logger.info(f'Friendship deleted: {instance}')
    except Exception as e:
        logger.error(f"Error deleting Friendship: {e}")
