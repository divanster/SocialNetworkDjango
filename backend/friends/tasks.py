from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_friend_event(friend_event_id, event_type, is_friendship=False):
    """
    Celery task to process friend events (friend requests or friendships) and send them to Kafka.
    """
    # Import models inside the function to prevent AppRegistryNotReady errors
    from .models import FriendRequest, Friendship

    producer = KafkaProducerClient()

    try:
        # Create message data for Kafka based on the type of event
        if event_type == 'deleted':
            message = {
                "friend_event_id": friend_event_id,
                "action": "deleted"
            }
        else:
            if is_friendship:
                # Fetch Friendship instance and create a message
                friendship = Friendship.objects.get(id=friend_event_id)
                message = {
                    "friendship_id": str(friendship.id),
                    "user1_id": friendship.user1.id,
                    "user2_id": friendship.user2.id,
                    "created_at": str(friendship.created_at),
                    "event": event_type
                }
            else:
                # Fetch FriendRequest instance and create a message
                friend_request = FriendRequest.objects.get(id=friend_event_id)
                message = {
                    "friend_request_id": str(friend_request.id),
                    "sender_id": friend_request.sender.id,
                    "receiver_id": friend_request.receiver.id,
                    "status": friend_request.status,
                    "created_at": str(friend_request.created_at),
                    "event": event_type
                }

        # Get Kafka topic from settings
        kafka_topic = settings.KAFKA_TOPICS.get('FRIEND_EVENTS', 'default-friend-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for {event_type}: {message}")

        # Notify the involved users via WebSocket
        send_websocket_notifications(message, is_friendship)

    except (FriendRequest.DoesNotExist, Friendship.DoesNotExist) as e:
        logger.error(f"Friend event with ID {friend_event_id} does not exist. Error: {e}")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


def send_websocket_notifications(message, is_friendship):
    """
    Sends WebSocket notifications to the users involved in the friendship or friend request.
    """
    try:
        from websocket.consumers import GeneralKafkaConsumer  # Import inside function to avoid circular dependencies
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        if is_friendship:
            # Friendship event: notify both users
            user1_group_name = GeneralKafkaConsumer.generate_group_name(message['user1_id'])
            user2_group_name = GeneralKafkaConsumer.generate_group_name(message['user2_id'])

            # Notify both users about the friendship event
            async_to_sync(channel_layer.group_send)(
                user1_group_name,
                {
                    'type': 'friend_notification',
                    'message': f"New friendship event: {message}"
                }
            )

            async_to_sync(channel_layer.group_send)(
                user2_group_name,
                {
                    'type': 'friend_notification',
                    'message': f"New friendship event: {message}"
                }
            )

            logger.info(f"WebSocket notifications sent for friendship event: {message}")

        else:
            # Friend request event: notify sender and receiver
            sender_group_name = GeneralKafkaConsumer.generate_group_name(message['sender_id'])
            receiver_group_name = GeneralKafkaConsumer.generate_group_name(message['receiver_id'])

            # Notify the sender about the friend request event
            async_to_sync(channel_layer.group_send)(
                sender_group_name,
                {
                    'type': 'friend_notification',
                    'message': f"New friend request event: {message}"
                }
            )

            # Notify the receiver about the friend request event
            async_to_sync(channel_layer.group_send)(
                receiver_group_name,
                {
                    'type': 'friend_notification',
                    'message': f"New friend request event: {message}"
                }
            )

            logger.info(f"WebSocket notifications sent for friend request event: {message}")

    except Exception as e:
        logger.error(f"Error sending WebSocket notifications for friend event: {e}")
