# backend/friends/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FriendRequest, Friendship
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from kafka_app.producer import KafkaProducerClient  # Import Kafka producer client
import logging

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


# Initialize Kafka Producer Client
producer = KafkaProducerClient()


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

            # Send Kafka event for a new friend request
            message = {
                "friend_request_id": instance.id,
                "sender_id": instance.sender.id,
                "receiver_id": instance.receiver.id,
                "status": instance.status,
                "created_at": str(instance.created_at),
            }
            producer.send_message('FRIEND_EVENTS', message)
            logger.info(f"Sent Kafka message for new friend request: {message}")

        # Automatically create a friendship if the friend request is accepted
        if instance.status == 'accepted':
            friendship, created = Friendship.objects.get_or_create(
                user1=min(instance.sender, instance.receiver, key=lambda u: u.id),
                user2=max(instance.sender, instance.receiver, key=lambda u: u.id),
            )
            if created:
                logger.info(
                    f'Friendship created automatically after friend request acceptance: {friendship}')

                # Send Kafka event for the accepted friendship
                message = {
                    "friendship_id": friendship.id,
                    "user1_id": friendship.user1.id,
                    "user2_id": friendship.user2.id,
                    "created_at": str(friendship.created_at),
                }
                producer.send_message('FRIEND_EVENTS', message)
                logger.info(f"Sent Kafka message for new friendship: {message}")
    except Exception as ex:
        logger.error(f"Unexpected error in friend_request_saved: {ex}")


@receiver(post_delete, sender=FriendRequest)
def friend_request_deleted(sender, instance, **kwargs):
    try:
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

        # Send Kafka event for the deleted friend request
        message = {
            "friend_request_id": instance.id,
            "action": "deleted"
        }
        producer.send_message('FRIEND_EVENTS', message)
        logger.info(f"Sent Kafka message for deleted friend request: {message}")
    except Exception as e:
        logger.error(f"Error deleting FriendRequest: {e}")


@receiver(post_save, sender=Friendship)
def friendship_saved(sender, instance, created, **kwargs):
    if created:
        try:
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

            # Send Kafka event for the new friendship
            message = {
                "friendship_id": instance.id,
                "user1_id": instance.user1.id,
                "user2_id": instance.user2.id,
                "created_at": str(instance.created_at),
            }
            producer.send_message('FRIEND_EVENTS', message)
            logger.info(f"Sent Kafka message for new friendship: {message}")
        except Exception as e:
            logger.error(f"Error creating Friendship: {e}")


@receiver(post_delete, sender=Friendship)
def friendship_deleted(sender, instance, **kwargs):
    try:
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

        # Send Kafka event for the deleted friendship
        message = {
            "friendship_id": instance.id,
            "action": "deleted"
        }
        producer.send_message('FRIEND_EVENTS', message)
        logger.info(f"Sent Kafka message for deleted friendship: {message}")
    except Exception as e:
        logger.error(f"Error deleting Friendship: {e}")
