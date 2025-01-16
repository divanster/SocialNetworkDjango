# backend/kafka_app/tasks/follow_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from kafka_app.constants import FOLLOW_EVENTS, FOLLOW_CREATED, FOLLOW_DELETED
from follows.models import Follow  # Ensure correct model import

logger = logging.getLogger(__name__)


def _get_follow_data(follow):
    """
    Extract relevant data from the follow instance.
    """
    return {
        'id': str(follow.id),  # Include 'id' within 'data'
        'follower_id': str(follow.follower.id),
        'follower_username': follow.follower.username,
        'followed_id': str(follow.followed.id),
        'followed_username': follow.followed.username,
        'created_at': follow.created_at.isoformat(),
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=3, default_retry_delay=60)
def process_follow_event_task(self, follow_id, event_type):
    """
    Celery task to process follow events and send messages to Kafka.

    Args:
        self: Celery task instance.
        follow_id (int): ID of the follow event.
        event_type (str): Type of the event, either FOLLOW_CREATED or FOLLOW_DELETED.

    Returns:
        None
    """
    try:
        follow = Follow.objects.get(id=follow_id)

        # Construct the standardized Kafka message
        if event_type == FOLLOW_DELETED:
            message = {
                'app': follow._meta.app_label,
                'event_type': event_type,
                'model_name': 'Follow',
                'id': str(follow_id),
                'data': {}  # Empty data for deleted events
            }
        else:
            message = {
                'app': follow._meta.app_label,
                'event_type': event_type,
                'model_name': 'Follow',
                'id': str(follow.id),
                'data': _get_follow_data(follow),
            }

        # Send message to Kafka using KafkaService
        kafka_topic_key = FOLLOW_EVENTS    # Use constant from constants.py
        KafkaService().send_message(kafka_topic_key, message)  # Pass the key directly
        logger.info(f"[KAFKA] Successfully sent follow {event_type} event to topic '{kafka_topic_key}': {message}")

    except Follow.DoesNotExist:
        logger.error(f"[KAFKA] Follow with ID {follow_id} does not exist. Cannot send {event_type} event.")
    except KafkaTimeoutError as e:
        logger.error(f"[KAFKA] Kafka timeout error while sending follow {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[KAFKA] Error sending follow {event_type} event to Kafka for follow ID {follow_id}: {e}")
        self.retry(exc=e, countdown=60)
