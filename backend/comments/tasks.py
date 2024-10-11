# backend/comments/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from .models import Comment
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_comment_event_to_kafka(comment_id, event_type):
    """
    Celery task to send comment events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "comment_id": comment_id,
                "action": "deleted"
            }
        else:
            comment = Comment.objects.get(id=comment_id)
            message = {
                "comment_id": comment.id,
                "content": comment.content,
                "user_id": comment.user_id,
                "post_id": comment.post_id,
                "created_at": str(comment.created_at),
                "event": event_type
            }

        producer.send_message('COMMENT_EVENTS', message)
        logger.info(f"Sent Kafka message for comment {event_type}: {message}")
    except Comment.DoesNotExist:
        logger.error(f"Comment with ID {comment_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
