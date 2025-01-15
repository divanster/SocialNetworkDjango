# backend/kafka_app/tasks/comment_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.choices import VisibilityChoices
from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from comments.models import Comment  # Ensure correct model import

logger = logging.getLogger(__name__)


def _get_comment_data(comment):
    """
    Extract relevant data from the comment instance.
    """
    return {
        'id': str(comment.id),  # Include 'id' within 'data'
        'user_id': str(comment.user.id),
        'username': comment.user.username,
        'post_id': str(comment.post.id),
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_comment_event_task(self, comment_id, event_type):
    """
    Celery task to process comment events and send messages to Kafka.

    Args:
        self: Celery task instance.
        comment_id (str): The ID of the comment.
        event_type (str): Type of event to be processed (e.g., "created", "updated", "deleted").

    Returns:
        None
    """
    try:
        comment = Comment.objects.get(pk=comment_id)

        # Respect visibility of the parent post or album if applicable
        if comment.post.album.visibility == VisibilityChoices.PRIVATE:
            logger.info(f"[TASK] Skipping Kafka message for comment in private album with ID {comment_id}")
            return

        # Construct the standardized Kafka message
        message = {
            'app': comment._meta.app_label,    # e.g., 'comments'
            'event_type': event_type,          # e.g., 'created'
            'model_name': 'Comment',           # Name of the model
            'id': str(comment.id),             # UUID as string
            'data': _get_comment_data(comment),# Event-specific data
        }

        # Send message to Kafka using KafkaService
        kafka_topic_key = 'COMMENT_EVENTS'    # Ensure this key exists in settings.KAFKA_TOPICS
        KafkaService().send_message(kafka_topic_key, message)  # Pass the key directly
        logger.info(f"[TASK] Successfully sent Kafka message for comment event '{event_type}': {message}")

    except Comment.DoesNotExist:
        logger.error(f"[TASK] Comment with ID {comment_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout error while sending comment '{event_type}': {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[TASK] Error sending Kafka message for comment '{comment_id}': {e}")
        self.retry(exc=e, countdown=60)
