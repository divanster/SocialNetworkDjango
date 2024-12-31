# backend/comments/tasks.py

import logging
from celery import shared_task

from django.conf import settings

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask)
def send_comment_event_to_kafka(self, comment_id, event_type):
    """
    Celery task to send comment events to Kafka.
    """
    try:
        from comments.models import Comment

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

        kafka_topic = settings.KAFKA_TOPICS.get('COMMENT_EVENTS',
                                                'default-comment-topic')
        KafkaProducerClient.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for comment {event_type}: {message}")

    except Comment.DoesNotExist:
        logger.error(f"Comment with ID {comment_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)
