# backend/messenger/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from kafka_app.consumer import KafkaConsumerClient
from django.conf import settings
from .models import Message
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_message_event_to_kafka(message_id, event_type):
    """
    Celery task to send message events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "message_id": message_id,
                "action": "deleted"
            }
        else:
            message_instance = Message.objects.get(id=message_id)
            message = {
                "message_id": message_instance.id,
                "content": message_instance.content,
                "user_id": message_instance.user.id,
                "created_at": str(message_instance.created_at),
                "event": event_type
            }

        # Use configured Kafka topic from Django settings
        kafka_topic = settings.KAFKA_TOPICS.get('MESSENGER_EVENTS', 'default-messenger-topic')
        producer.send_message(kafka_topic, message)

        logger.info(f"Sent Kafka message for message {event_type}: {message}")
    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


@shared_task
def consume_message_events():
    """
    Celery task to consume message events from Kafka.
    """
    kafka_topic = settings.KAFKA_TOPICS.get('MESSENGER_EVENTS', 'default-messenger-topic')
    consumer = KafkaConsumerClient(kafka_topic)

    for message in consumer.consume_messages():
        try:
            # Add message-specific processing logic here
            logger.info(f"Processed message event: {message}")
            # Example: Notify users of a new message, update message analytics, etc.
        except Exception as e:
            logger.error(f"Error processing message event: {e}")
