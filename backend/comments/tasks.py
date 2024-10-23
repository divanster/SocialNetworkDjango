# backend/comments/tasks.py
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
from .models import Comment
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def send_comment_event_to_kafka(self, comment_id, event_type):
    """
    Celery task to send comment events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "event": "deleted",
                "comment_id": comment_id
            }
        else:
            comment = Comment.objects.get(id=comment_id)
            message = {
                "event": event_type,
                "comment_id": comment.id,
                "content": comment.content,
                "user_id": comment.user_id,
                "post_id": comment.post_id,
                "created_at": str(comment.created_at),
            }

        kafka_topic = settings.KAFKA_TOPICS.get('COMMENT_EVENTS',
                                                'default-comment-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"[TASK] Sent Kafka message for comment {event_type}: {message}")
    except Comment.DoesNotExist:
        logger.error(f"Comment with ID {comment_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
