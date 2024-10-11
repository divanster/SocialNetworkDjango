# backend/pages/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from kafka_app.consumer import KafkaConsumerClient
from .models import Page
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_page_event_to_kafka(page_id, event_type):
    """
    Celery task to send page events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "page_id": page_id,
                "action": "deleted"
            }
        else:
            page = Page.objects.get(id=page_id)
            message = {
                "page_id": page.id,
                "title": page.title,
                "content": page.content,
                "created_at": str(page.created_at),
                "event": event_type,
            }

        producer.send_message('PAGE_EVENTS', message)
        logger.info(f"Sent Kafka message for page {event_type}: {message}")
    except Page.DoesNotExist:
        logger.error(f"Page with ID {page_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


@shared_task
def consume_page_events():
    """
    Celery task to consume page events from Kafka.
    """
    topic = settings.KAFKA_TOPICS.get('PAGE_EVENTS', 'default-page-topic')
    consumer = KafkaConsumerClient(topic)
    for message in consumer.consume_messages():
        try:
            # Add page-specific processing logic here
            logger.info(f"Processed page event: {message}")
        except Exception as e:
            logger.error(f"Error processing page event: {e}")
