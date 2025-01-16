# backend/kafka_app/tasks/social_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from kafka_app.constants import SOCIAL_EVENTS, POST_CREATED, POST_UPDATED, POST_DELETED
from social.models import Post  # Ensure correct model import

logger = logging.getLogger(__name__)


def _get_post_data(post):
    """
    Extract relevant data from the post instance.
    """
    return {
        'id': str(post.id),              # Include 'id' within 'data'
        'content': post.content,
        'title': post.title,
        'user_id': str(post.user.id),
        'user_username': post.user.username,
        'visibility': post.visibility,
        'created_at': post.created_at.isoformat(),
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_post_event_task(self, post_id, event_type):
    """
    Celery task to process post events and send messages to Kafka.

    Args:
        self: Celery task instance.
        post_id (str): The ID of the post.
        event_type (str): Type of event to be processed (e.g., POST_CREATED, POST_UPDATED, POST_DELETED).

    Returns:
        None
    """
    try:
        post = Post.objects.get(pk=post_id)

        # Construct the standardized Kafka message
        message = {
            'app': post._meta.app_label,      # e.g., 'social'
            'event_type': event_type,          # e.g., POST_CREATED
            'model_name': 'Post',              # Name of the model
            'id': str(post.id),                # UUID as string
            'data': _get_post_data(post),      # Event-specific data
        }

        # Send message to Kafka using KafkaService
        kafka_topic_key = SOCIAL_EVENTS    # Use constant from constants.py
        KafkaService().send_message(kafka_topic_key, message)  # Pass the key directly
        logger.info(f"[TASK] Successfully sent Kafka message for post event '{event_type}': {message}")

    except Post.DoesNotExist:
        logger.error(f"[TASK] Post with ID {post_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout occurred while processing post {post_id} for event {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[TASK] Unexpected error occurred while sending Kafka message for post {post_id}: {e}")
        self.retry(exc=e, countdown=60)
