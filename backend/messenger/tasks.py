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
                "sender_id": message_instance.sender_id,
                "sender_username": message_instance.sender_username,
                "receiver_id": message_instance.receiver_id,
                "receiver_username": message_instance.receiver_username,
                "content": message_instance.content,
                "timestamp": str(message_instance.timestamp),
                "event": event_type
            }

        # Use configured Kafka topic from Django settings
        kafka_topic = settings.KAFKA_TOPICS.get('MESSENGER_EVENTS', 'default-messenger-topic')
        producer.send_message(kafka_topic, message)

        producer.close()
        logger.info(f"Sent Kafka message for message {event_type}: {message}")
    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


def process_message_event(message):
    """
    Process each message received from Kafka.
    Add logic to handle different message events here, such as updating UI,
    notifying users, or saving messages.
    """
    event_type = message.get("event")
    try:
        if event_type == "created":
            # Handle new message creation logic if needed, such as notifying users
            logger.info(f"New message created event: {message}")
        elif event_type == "updated":
            # Handle message updates, such as marking messages as read
            logger.info(f"Message updated event: {message}")
        elif event_type == "deleted":
            # Handle deletion logic
            message_id = message.get("message_id")
            if message_id:
                Message.objects.filter(id=message_id).delete()
                logger.info(f"Message with ID {message_id} deleted successfully.")
        else:
            logger.warning(f"Unknown event type: {event_type}")
    except Exception as e:
        logger.error(f"Error processing message event {message}: {e}")
