from celery import shared_task
from kafka_app.consumer import KafkaConsumerClient
from kafka_app.producer import KafkaProducerClient
from .models import Notification
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_notification_event_to_kafka(self, notification_id, event_type):
    """
    Celery task to send notification events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "notification_id": notification_id,
                "action": "deleted"
            }
        else:
            notification = Notification.objects.get(id=notification_id)
            message = {
                "notification_id": notification.id,
                "sender_id": notification.sender_id,
                "receiver_id": notification.receiver_id,
                "notification_type": notification.notification_type,
                "text": notification.text,
                "created_at": str(notification.created_at),
                "event": event_type,
            }

        producer.send_message('NOTIFICATIONS_EVENTS', message)
        logger.info(f"Sent Kafka message for notification {event_type}: {message}")
    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)
