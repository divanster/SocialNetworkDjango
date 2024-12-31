# backend/kafka_app/tasks/tagging_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def send_tagging_event_to_kafka(self, tagged_item_id, event_type):
    """
    Celery task to send tagging events to Kafka.

    Args:
        self: Celery task instance.
        tagged_item_id (int): The ID of the TaggedItem.
        event_type (str): Type of event (e.g., "created", "deleted").

    Returns:
        None
    """
    try:
        from tagging.models import TaggedItem  # Local import to prevent circular dependencies
        producer = KafkaProducerClient()

        if event_type == 'deleted':
            message = {
                "tagged_item_id": tagged_item_id,
                "event": "deleted"
            }
        else:
            tagged_item = TaggedItem.objects.select_related('tagged_user', 'tagged_by').get(id=tagged_item_id)
            message = {
                "tagged_item_id": tagged_item.id,
                "tagged_user_id": str(tagged_item.tagged_user.id),
                "content_type": str(tagged_item.content_type),
                "object_id": str(tagged_item.object_id),
                "tagged_by_id": str(tagged_item.tagged_by.id),
                "created_at": tagged_item.created_at.isoformat(),
                "event": event_type,
            }

        kafka_topic = settings.KAFKA_TOPICS.get('TAGGING_EVENTS', 'tagging-events')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for tagging event {event_type}: {message}")

    except TaggedItem.DoesNotExist:
        logger.error(f"TaggedItem with ID {tagged_item_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending tagging {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def consume_tagging_events(self):
    """
    Celery task to consume tagging events from Kafka.
    """
    try:
        # Placeholder implementation
        logger.warning("The consume_tagging_events task is not implemented.")
        # Implement Kafka consumer logic here if needed
    except Exception as e:
        logger.error(f"Error consuming tagging events: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
