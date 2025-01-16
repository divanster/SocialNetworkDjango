# backend/kafka_app/tasks/notification_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.utils import timezone
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from kafka_app.constants import NOTIFICATIONS, NOTIFICATION_SENT, NOTIFICATION_DELETED
from notifications.models import Notification  # Ensure correct model import

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_notification_event_task(self, notification_id, event_type):
    """
    Celery task to process notification events and send them to Kafka.

    Args:
        self: Celery task instance.
        notification_id (UUID): The UUID of the notification.
        event_type (str): Type of event (e.g., NOTIFICATION_SENT, NOTIFICATION_DELETED).

    Returns:
        None
    """
    try:
        # Prepare the message based on the event type
        if event_type == NOTIFICATION_DELETED:
            message = {
                'app': 'notifications',  # Assuming the app label is 'notifications'
                'event_type': event_type,
                'model_name': 'Notification',
                'id': str(notification_id),
                'data': {
                    'deleted_at': timezone.now().isoformat()
                }
            }
        else:
            # Retrieve the notification instance
            notification = Notification.objects.select_related('sender', 'receiver').get(id=notification_id)
            message = {
                'app': notification._meta.app_label,
                'event_type': event_type,
                'model_name': 'Notification',
                'id': str(notification.id),
                'data': {
                    'notification_id': str(notification.id),
                    'sender_id': str(notification.sender.id),
                    'sender_username': notification.sender.username,
                    'receiver_id': str(notification.receiver.id),
                    'receiver_username': notification.receiver.username,
                    'notification_type': notification.notification_type,
                    'text': notification.text,
                    'created_at': notification.created_at.isoformat(),
                    'updated_at': notification.updated_at.isoformat(),
                    'is_read': notification.is_read,
                }
            }

        # Send message to Kafka using KafkaService
        kafka_topic_key = NOTIFICATIONS  # Use constant from constants.py
        kafka_topic = settings.KAFKA_TOPICS.get(kafka_topic_key, 'notifications')  # Fallback to 'notifications'
        KafkaService().send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for notification {event_type}: {message}")

    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending notification {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
