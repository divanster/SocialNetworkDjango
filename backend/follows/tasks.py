# backend/follows/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
from .models import Follow
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_follow_event_task(self, follow_id, event_type):
    """
    Celery task to process follow events and send them to Kafka.

    This function attempts to send information about a follow event (created or deleted)
    to a Kafka topic using a Kafka producer. In case of failure, it retries the operation.

    Args:
        follow_id (int): ID of the follow event.
        event_type (str): Type of the event, either 'created' or 'deleted'.

    Raises:
        self.retry: Retries the task in case of an exception.
    """
    producer = KafkaProducerClient()

    try:
        # Construct the message based on the event type
        if event_type == 'deleted':
            message = {
                "follow_id": follow_id,
                "action": "deleted"
            }
        else:
            follow = Follow.objects.get(id=follow_id)
            message = {
                "follow_id": follow.id,
                "follower_id": follow.follower.id,
                "follower_username": follow.follower.username,
                "followed_id": follow.followed.id,
                "followed_username": follow.followed.username,
                "created_at": str(follow.created_at),
                "event": event_type
            }

        # Get Kafka topic from settings for better flexibility
        kafka_topic = settings.KAFKA_TOPICS.get('FOLLOW_EVENTS', 'default-follow-topic')

        # Send message to Kafka
        producer.send_message(kafka_topic, message)

        logger.info(
            f"[KAFKA] Successfully sent follow {event_type} event to topic '{kafka_topic}': {message}")

    except Follow.DoesNotExist:
        logger.error(
            f"[KAFKA] Follow with ID {follow_id} does not exist. Cannot send {event_type} event.")
    except Exception as e:
        logger.error(
            f"[KAFKA] Error sending follow {event_type} event to Kafka for follow ID {follow_id}: {e}")
        # Retry the task in case of failure, with exponential backoff
        raise self.retry(exc=e, countdown=60)
