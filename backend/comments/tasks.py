# backend/comments/tasks.py
from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from kafka_app.consumer import KafkaConsumerClient
from django.conf import settings
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
                "user_id": comment.user.id,
                "post_id": comment.post.id,
                "created_at": str(comment.created_at),
                "event": event_type
            }

        kafka_topic = settings.KAFKA_TOPICS.get('COMMENT_EVENTS', 'default-comment-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for comment {event_type}: {message}")
    except Comment.DoesNotExist:
        logger.error(f"Comment with ID {comment_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        raise e


@shared_task
def consume_comment_events():
    """
    Celery task to consume comment events from Kafka.
    """
    kafka_topic = settings.KAFKA_TOPICS.get('COMMENT_EVENTS', 'default-comment-topic')
    consumer = KafkaConsumerClient(kafka_topic)

    for message in consumer.consume_messages():
        try:
            logger.info(f"Processed comment event: {message}")
        except Exception as e:
            logger.error(f"Error processing comment event: {e}")
