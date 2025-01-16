# backend/kafka_app/tasks/friend_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from kafka_app.constants import FRIEND_EVENTS, FRIEND_ADDED, FRIEND_REMOVED
from friends.models import FriendRequest, Friendship

logger = logging.getLogger(__name__)


def _get_friendship_data(friendship):
    """
    Extract relevant data from the friendship instance.
    """
    return {
        'friendship_id': str(friendship.id),
        'user1_id': str(friendship.user1.id),
        'user1_username': friendship.user1.username,
        'user2_id': str(friendship.user2.id),
        'user2_username': friendship.user2.username,
        'created_at': friendship.created_at.isoformat(),
        # Add other relevant fields as needed
    }


def _get_friend_request_data(friend_request):
    """
    Extract relevant data from the friend request instance.
    """
    return {
        'friend_request_id': str(friend_request.id),
        'sender_id': str(friend_request.sender.id),
        'sender_username': friend_request.sender.username,
        'receiver_id': str(friend_request.receiver.id),
        'receiver_username': friend_request.receiver.username,
        'status': friend_request.status,
        'created_at': friend_request.created_at.isoformat(),
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_friend_event_task(self, friend_event_id, event_type, is_friendship=False):
    """
    Celery task to process friend events (friend requests or friendships) and send them to Kafka.

    Args:
        self: Celery task instance.
        friend_event_id (UUID): ID of the friend event.
        event_type (str): Type of the event, e.g., FRIEND_ADDED, FRIEND_REMOVED.
        is_friendship (bool): Indicates if the event is a friendship or a friend request.

    Returns:
        None
    """
    try:
        if is_friendship:
            friendship = Friendship.objects.get(id=friend_event_id)
            data = _get_friendship_data(friendship)
            model_name = 'Friendship'
        else:
            friend_request = FriendRequest.objects.get(id=friend_event_id)
            data = _get_friend_request_data(friend_request)
            model_name = 'FriendRequest'

        # Construct the standardized Kafka message
        message = {
            'app': 'friends',  # Assuming the app label is 'friends'
            'event_type': event_type,
            'model_name': model_name,
            'id': str(friend_event_id),
            'data': data,
        }

        # Send message to Kafka using KafkaService
        kafka_topic_key = FRIEND_EVENTS  # Use constant from constants.py
        KafkaService().send_message(kafka_topic_key, message)
        logger.info(f"Sent Kafka message for {event_type}: {message}")

    except (FriendRequest.DoesNotExist, Friendship.DoesNotExist) as e:
        logger.error(f"Friend event with ID {friend_event_id} does not exist. Error: {e}")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending friend {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
