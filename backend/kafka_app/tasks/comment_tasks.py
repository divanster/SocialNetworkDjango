# backend/kafka_app/tasks/comment_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


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
        from comments.models import Comment  # Local import to prevent circular dependencies
        producer = KafkaProducerClient()

        if event_type == 'deleted':
            message = {
                "comment_id": comment_id,
                "action": "deleted"
            }
        else:
            comment = Comment.objects.select_related('user', 'post').get(id=comment_id)
            message = {
                "comment_id": comment.id,
                "user_id": str(comment.user.id),
                "post_id": str(comment.post.id),
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "event": event_type,
            }

        kafka_topic = settings.KAFKA_TOPICS.get('COMMENT_EVENTS', 'comment-events')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for comment {event_type}: {message}")

    except Comment.DoesNotExist:
        logger.error(f"Comment with ID {comment_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending comment {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
