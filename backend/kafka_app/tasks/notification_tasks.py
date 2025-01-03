# backend/kafka_app/tasks/notification_tasks.py


from celery import shared_task

from core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient
from kafka.errors import KafkaTimeoutError

import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_notification_event_task(self, notification_id, event_type):
    """
    Celery task to process notification events and send them to Kafka.
    """
    producer = None  # Initialize producer as None to handle any initialization errors

    try:
        # Dynamically import the Notification model to avoid AppRegistryNotReady issues.
        from notifications.models import Notification

        # Prepare the message based on the event type
        if event_type == 'deleted':
            message = {
                "notification_id": notification_id,
                "action": "deleted"
            }
        else:
            # Retrieve the notification instance
            notification = Notification.objects.get(id=notification_id)
            message = {
                "notification_id": notification.id,
                "sender_id": notification.sender_id,
                "sender_username": notification.sender_username,
                "receiver_id": notification.receiver_id,
                "receiver_username": notification.receiver_username,
                "notification_type": notification.notification_type,
                "text": notification.text,
                "created_at": str(notification.created_at),
                "event": event_type,
            }

        # Initialize the Kafka producer and send the message
        producer = KafkaProducerClient()
        kafka_topic = 'NOTIFICATIONS_EVENTS'
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for notification {event_type}: {message}")

    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending notification {event_type}: {e}")
        self.retry(exc=e)
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)
    finally:
        # Ensure that the producer is properly closed if it was created
        if producer:
            try:
                producer.close()
            except Exception as e:
                logger.error(f"Error while closing Kafka producer: {e}")
