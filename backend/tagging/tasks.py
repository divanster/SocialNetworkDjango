# backend/tagging/tasks.py

import logging
from celery import shared_task

from django.conf import settings

from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_tagging_event_to_kafka(self, tagged_item_id, event_type):
    """
    Celery task to send tagging events to Kafka.
    """
    try:
        from .models import TaggedItem  # Local import to prevent circular dependencies

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

        kafka_topic = settings.KAFKA_TOPICS.get('TAGGING_EVENTS', 'default-tagging-topic')
        KafkaProducerClient.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for tagging event {event_type}: {message}")

    except TaggedItem.DoesNotExist:
        logger.error(f"TaggedItem with ID {tagged_item_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
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
        self.retry(exc=e)
