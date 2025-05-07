import logging
from celery import shared_task
from aiokafka.errors import KafkaTimeoutError

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
        'id': str(post.id),  # Include 'id' within 'data'
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
    """
    logger.debug(f"Received event_type: {event_type} for post {post_id}")  # Log event_type

    try:
        # Validate event_type
        valid_event_types = [POST_CREATED, POST_UPDATED, POST_DELETED]
        if event_type not in valid_event_types:
            logger.error(f"Invalid event_type '{event_type}' for post {post_id}")
            return  # Early return if event_type is invalid

        post = Post.objects.get(pk=post_id)
        logger.debug(f"Fetched post with ID {post_id}: {post}")

        # Handle different event types (currently no-op but can be added)
        if event_type == POST_CREATED:
            pass
        elif event_type == POST_UPDATED:
            pass
        elif event_type == POST_DELETED:
            pass

        # Create Kafka message
        message = {
            'app': post._meta.app_label,
            'event_type': event_type,  # Ensure event_type is included
            'model_name': 'Post',
            'id': str(post.id),
            'data': _get_post_data(post),
        }

        logger.debug(f"Kafka message: {message}")  # Log Kafka message for debugging

        # Send message to Kafka using KafkaService
        kafka_topic_key = SOCIAL_EVENTS
        KafkaService().send_message(kafka_topic_key, message)
        logger.info(f"Successfully sent Kafka message for post event '{event_type}'.")

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error for post {post_id}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries), max_retries=5)
    except KafkaError as e:
        logger.error(f"Kafka error for post {post_id}: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)
    except Exception as e:
        logger.error(f"Unexpected error processing post {post_id}: {e}")
        self.retry(exc=e, countdown=60)
