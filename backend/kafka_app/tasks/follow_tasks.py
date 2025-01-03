# backend/kafka_app/tasks/follow_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=3, default_retry_delay=60)
def process_follow_event_task(self, follow_id, event_type):
    """
    Celery task to process follow events and send them to Kafka.

    Args:
        self: Celery task instance.
        follow_id (int): ID of the follow event.
        event_type (str): Type of the event, either 'created' or 'deleted'.

    Raises:
        self.retry: Retries the task in case of an exception.
    """
    try:
        from follows.models import Follow  # Local import to avoid AppRegistryNotReady errors
        producer = KafkaProducerClient()

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
        kafka_topic = settings.KAFKA_TOPICS.get('FOLLOW_EVENTS', 'follow-events')

        # Send message to Kafka
        producer.send_message(kafka_topic, message)

        logger.info(f"[KAFKA] Successfully sent follow {event_type} event to topic '{kafka_topic}': {message}")

    except Follow.DoesNotExist:
        logger.error(f"[KAFKA] Follow with ID {follow_id} does not exist. Cannot send {event_type} event.")
    except KafkaTimeoutError as e:
        logger.error(f"[KAFKA] Kafka timeout error while sending follow {event_type} event for follow ID {follow_id}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[KAFKA] Error sending follow {event_type} event to Kafka for follow ID {follow_id}: {e}")
        self.retry(exc=e, countdown=60)
