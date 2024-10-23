# messenger/tasks.py

from celery import shared_task
from django.conf import settings
from .models import Message
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def process_message_event_task(self, message_id, event_type):
    """
    Celery task to process message events and send them to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "message_id": message_id,
                "action": "deleted"
            }
        else:
            # Fetch the message instance to create the message payload
            message_instance = Message.objects.get(id=message_id)
            message = {
                "message_id": str(message_instance.id),
                "sender_id": str(message_instance.sender.id),
                "sender_username": message_instance.sender.username,
                "receiver_id": str(message_instance.receiver.id),
                "receiver_username": message_instance.receiver.username,
                "content": message_instance.content,
                "timestamp": str(message_instance.timestamp),
                "event": event_type
            }

        # Get Kafka topic from settings
        kafka_topic = settings.KAFKA_TOPICS.get('MESSENGER_EVENTS',
                                                'default-messenger-topic')
        producer.send_message(kafka_topic, message)

        logger.info(f"Sent Kafka message for message {event_type}: {message}")

    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e,
                   countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    finally:
        producer.close()  # Ensure the producer is properly closed
