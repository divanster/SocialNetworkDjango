# backend/tagging/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
from .models import TaggedItem
import logging
import json

logger = logging.getLogger(__name__)


@shared_task
def send_tagging_event_to_kafka(tagged_item_id, event_type):
    """
    Celery task to send tagging events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "tagged_item_id": tagged_item_id,
                "event": "deleted"
            }
        else:
            tagged_item = TaggedItem.objects.get(id=tagged_item_id)
            message = {
                "tagged_item_id": tagged_item.id,
                "tagged_user_id": tagged_item.tagged_user.id,
                "content_type": str(tagged_item.content_type),
                "object_id": tagged_item.object_id,
                "tagged_by_id": tagged_item.tagged_by.id,
                "created_at": str(tagged_item.created_at),
                "event": event_type,
            }

        # Get Kafka topic from settings
        kafka_topic = settings.KAFKA_TOPICS.get('TAGGING_EVENTS', 'default-tagging-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for tagging event {event_type}: {message}")
    except TaggedItem.DoesNotExist:
        logger.error(f"TaggedItem with ID {tagged_item_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
    finally:
        producer.close()  # Ensure producer is closed to free resources.


@shared_task
def consume_tagging_events():
    """
    Celery task to consume tagging events from Kafka.
    """
    try:
        # Placeholder implementation, should be updated based on Kafka client
        logger.warning("The consume_tagging_events task is not implemented.")
    except Exception as e:
        logger.error(f"Error consuming tagging events: {e}")
