from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
from .models import FriendRequest, Friendship
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_friend_event(friend_event_id, event_type, is_friendship=False):
    """
    Celery task to process friend events (friend requests or friendships) and send them to Kafka.
    """
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
                    "friendship_id": friendship.id,
                    "user1_id": friendship.user1.id,
                    "user2_id": friendship.user2.id,
                    "created_at": str(friendship.created_at),
                    "event": event_type
                }
            else:
                # Fetch FriendRequest instance and create a message
                friend_request = FriendRequest.objects.get(id=friend_event_id)
                message = {
                    "friend_request_id": friend_request.id,
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

    except (FriendRequest.DoesNotExist, Friendship.DoesNotExist) as e:
        logger.error(f"Friend event with ID {friend_event_id} does not exist. Error: {e}")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
