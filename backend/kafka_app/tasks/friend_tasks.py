# backend/kafka_app/tasks/friend_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_friend_event(self, friend_event_id, event_type, is_friendship=False):
    """
    Celery task to process friend events (friend requests or friendships) and send them to Kafka.

    Args:
        self: Celery task instance.
        friend_event_id (int): ID of the friend event.
        event_type (str): Type of the event, e.g., 'created', 'deleted'.
        is_friendship (bool): Indicates if the event is a friendship or a friend request.

    Returns:
        None
    """
    try:
        from follows.models import FriendRequest, Friendship  # Local import to avoid AppRegistryNotReady errors
        producer = KafkaProducerClient()

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
        kafka_topic = settings.KAFKA_TOPICS.get('FRIEND_EVENTS', 'friend-events')
        producer.send_message(kafka_topic, message)

        logger.info(f"Sent Kafka message for {event_type}: {message}")

    except (FriendRequest.DoesNotExist, Friendship.DoesNotExist) as e:
        logger.error(f"Friend event with ID {friend_event_id} does not exist. Error: {e}")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending friend {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
