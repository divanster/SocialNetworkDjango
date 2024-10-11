# backend/tagging/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from kafka_app.consumer import KafkaConsumerClient
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
                "action": "deleted"
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

        producer.send_message('TAGGING_EVENTS', message)
        logger.info(f"Sent Kafka message for tagging event {event_type}: {message}")
    except TaggedItem.DoesNotExist:
        logger.error(f"TaggedItem with ID {tagged_item_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


@shared_task
def consume_tagging_events():
    """
    Celery task to consume tagging events from Kafka.
    """
    topic = settings.KAFKA_TOPICS.get('TAGGING_EVENTS', 'default-tagging-topic')
    consumer = KafkaConsumerClient(topic)
    for message in consumer.consume_messages():
        try:
            # Convert message to dictionary if it is a string
            if isinstance(message, str):
                message = json.loads(message)

            # Process tagging event logic here
            event_type = message.get('event')
            tagged_item_id = message.get('tagged_item_id')

            if event_type == 'created':
                logger.info(f"Processing 'created' tagging event for TaggedItem ID: {tagged_item_id}")
            elif event_type == 'deleted':
                logger.info(f"Processing 'deleted' tagging event for TaggedItem ID: {tagged_item_id}")
            else:
                logger.warning(f"Unknown tagging event type: {event_type}")

            logger.info(f"Processed tagging event: {message}")
        except Exception as e:
            logger.error(f"Error processing tagging event: {e}")
