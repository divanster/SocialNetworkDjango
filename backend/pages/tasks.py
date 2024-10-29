from celery import shared_task
from kafka_app.producer import KafkaProducerClient
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_page_event_to_kafka(self, page_id, event_type):
    """
    Celery task to send page events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        # Dynamically import the Page model
        from pages.models import Page

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
                "user_id": page.user.id,
                "user_username": page.user.username
            }

        # Send the constructed message to the PAGE_EVENTS Kafka topic
        kafka_topic = settings.KAFKA_TOPICS.get('PAGE_EVENTS', 'default-page-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for page {event_type}: {message}")

    except Page.DoesNotExist:
        logger.error(f"Page with ID {page_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
    finally:
        producer.close()  # Ensure the producer is properly closed
