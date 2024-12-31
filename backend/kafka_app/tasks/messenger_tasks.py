# backend/kafka_app/tasks/messenger_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_message_event_task(self, message_id, event_type):
    """
    Celery task to process message events and send them to Kafka.

    Args:
        self: Celery task instance.
        message_id (int): The ID of the message.
        event_type (str): Type of event (e.g., "created", "updated", "deleted").

    Returns:
        None
    """
    try:
        from messenger.models import Message  # Local import to avoid circular dependencies
        producer = KafkaProducerClient()

        if event_type == 'deleted':
            message = {
                "message_id": message_id,
                "event": "deleted"
            }
        else:
            message_instance = Message.objects.select_related('sender', 'receiver').get(id=message_id)
            message = {
                "message_id": str(message_instance.id),
                "sender_id": str(message_instance.sender.id),
                "sender_username": message_instance.sender.username,
                "receiver_id": str(message_instance.receiver.id),
                "receiver_username": message_instance.receiver.username,
                "content": message_instance.content,
                "timestamp": message_instance.timestamp.isoformat(),
                "event": event_type
            }

        kafka_topic = settings.KAFKA_TOPICS.get('MESSENGER_EVENTS', 'messenger-events')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for message {event_type}: {message}")

    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending message {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
