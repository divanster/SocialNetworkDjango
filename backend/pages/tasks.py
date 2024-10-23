# backend/pages/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
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
            # Prepare the message for deleted page event
            message = {
                "page_id": page_id,
                "action": "deleted"
            }
        else:
            # Prepare the message for created or updated page event
            page = Page.objects.get(id=page_id)
            message = {
                "page_id": page.id,
                "title": page.title,
                "content": page.content,
                "created_at": str(page.created_at),
                "event": event_type,
            }

        # Send the constructed message to the PAGE_EVENTS Kafka topic
        kafka_topic = settings.KAFKA_TOPICS.get('PAGE_EVENTS', 'default-page-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for page {event_type}: {message}")

    except Page.DoesNotExist:
        logger.error(f"Page with ID {page_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
    finally:
        producer.close()  # Ensure the producer is properly closed
