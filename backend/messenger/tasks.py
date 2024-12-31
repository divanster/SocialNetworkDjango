# backend/messenger/tasks.py

import logging
from celery import shared_task

from django.conf import settings

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask)
def send_message_event_to_kafka(self, message_id, event_type):
    """
    Celery task to send message events to Kafka.
    """
    try:
        from messenger.models import Message

        if event_type == 'deleted':
            message = {
                "message_id": message_id,
                "event": "deleted"
            }
        else:
            message_instance = Message.objects.select_related('sender', 'receiver').get(
                id=message_id)
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

        kafka_topic = settings.KAFKA_TOPICS.get('MESSENGER_EVENTS',
                                                'default-messenger-topic')
        KafkaProducerClient.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for message {event_type}: {message}")

    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)
