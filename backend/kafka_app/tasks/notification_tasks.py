import logging
from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from kafka.errors import KafkaTimeoutError
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def process_notification_event_task(self, notification_id, event_type):
    """
    Celery task to process notification events and send them to Kafka.

    Args:
        self: Celery task instance.
        notification_id (UUID): The UUID of the notification.
        event_type (str): Type of event (e.g., "created", "updated", "deleted").

    Returns:
        None
    """
    producer = None  # Initialize producer as None to handle any initialization errors

    try:
        # Dynamically import the Notification model to avoid AppRegistryNotReady issues.
        from notifications.models import Notification

        # Prepare the message based on the event type
        if event_type == 'deleted':
            message = {
                "notification_id": str(notification_id),
                "action": "deleted",
                "deleted_at": timezone.now().isoformat()
            }
        else:
            # Retrieve the notification instance
            notification = Notification.objects.select_related('sender', 'receiver').get(id=notification_id)
            message = {
                "notification_id": str(notification.id),
                "sender_id": str(notification.sender.id),
                "sender_username": notification.sender.username,
                "receiver_id": str(notification.receiver.id),
                "receiver_username": notification.receiver.username,
                "notification_type": notification.notification_type,
                "text": notification.text,
                "created_at": notification.created_at.isoformat(),
                "updated_at": notification.updated_at.isoformat(),
                "is_read": notification.is_read,
                "event": event_type,
            }

        # Initialize the Kafka producer and send the message
        producer = KafkaProducerClient()
        kafka_topic = settings.KAFKA_TOPICS.get('NOTIFICATIONS_EVENTS', 'notifications-events')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for notification {event_type}: {message}")

    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(
            f"Kafka timeout error while sending notification {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
    finally:
        # Ensure that the producer is properly closed if it was created
        if producer:
            try:
                producer.close()
                logger.debug("Kafka producer closed successfully.")
            except Exception as e:
                logger.error(f"Error while closing Kafka producer: {e}")
