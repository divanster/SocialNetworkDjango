# backend/kafka_app/tasks/social_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from social.models import Post  # Example model import

logger = logging.getLogger(__name__)


def _get_post_data(post):
    """
    Extract relevant data from the post instance.
    """
    return {
        'content': post.content,
        'created_at': post.created_at.isoformat(),
        'title': post.title,
        'user_id': str(post.user.id),
        'user_username': post.user.username,
        'visibility': post.visibility,
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_post_event_task(self, post_id, event_type):
    """
    Celery task to process post events and send messages to Kafka.

    Args:
        self: Celery task instance.
        post_id (UUID): The ID of the post.
        event_type (str): Type of event to be processed (e.g., "created", "updated", "deleted").

    Returns:
        None
    """
    try:
        post = Post.objects.get(id=post_id)

        # Construct the standardized Kafka message
        message = {
            'app': post._meta.app_label,
            'event_type': event_type,
            'model_name': 'Post',
            'id': str(post.id),
            'data': _get_post_data(post),
        }

        # Send message to Kafka using KafkaService
        kafka_topic_key = 'SOCIAL_EVENTS'  # Ensure this key exists in settings.KAFKA_TOPICS
        KafkaService().send_message(kafka_topic_key, message)
        logger.info(f"Sent Kafka message for post {event_type}: {message}")

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending post {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
