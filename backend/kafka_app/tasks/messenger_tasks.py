# backend/kafka_app/tasks/messenger_tasks.py

import logging
from celery import shared_task
from aiokafka.errors import KafkaTimeoutError
from django.conf import settings
from django.utils import timezone

from core.task_utils import BaseTask
from kafka_app.constants import MESSENGER_EVENTS, MESSAGE_CREATED, MESSAGE_UPDATED, MESSAGE_DELETED
from kafka_app.services import KafkaService
from messenger.models import Message  # Ensure correct model import

logger = logging.getLogger(__name__)


def _get_message_data(message_instance):
    """
    Extract relevant data from the message instance.
    """
    return {
        'message_id': str(message_instance.id),
        'sender_id': str(message_instance.sender.id),
        'sender_username': message_instance.sender.username,
        'receiver_id': str(message_instance.receiver.id),
        'receiver_username': message_instance.receiver.username,
        'content': message_instance.content,
        'created_at': message_instance.created_at.isoformat(),
        'updated_at': message_instance.updated_at.isoformat(),
        'is_read': message_instance.is_read,
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_message_event_task(self, message_id, event_type):
    """
    Celery task to process message events and send them to Kafka.

    Args:
        self: Celery task instance.
        message_id (UUID): The UUID of the message.
        event_type (str): Type of event (e.g., MESSAGE_CREATED, MESSAGE_UPDATED, MESSAGE_DELETED).

    Returns:
        None
    """
    try:
        if event_type == MESSAGE_DELETED:
            # Create a message for deleted events with just the object ID and event type
            message = {
                'app': 'messenger',  # Assuming the app label is 'messenger'
                'event_type': event_type,
                'model_name': 'Message',
                'id': str(message_id),
                'data': {
                    'deleted_at': timezone.now().isoformat()
                }
            }
        else:
            message_instance = Message.objects.select_related('sender', 'receiver').get(id=message_id)
            message = {
                'app': message_instance._meta.app_label,
                'event_type': event_type,
                'model_name': 'Message',
                'id': str(message_instance.id),
                'data': _get_message_data(message_instance),
            }

        # Send message to Kafka using KafkaService
        kafka_topic_key = MESSENGER_EVENTS  # Use constant from constants.py
        KafkaService().send_message(kafka_topic_key, message)  # Pass the key directly
        logger.info(f"Sent Kafka message for message {event_type}: {message}")

    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending message {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
