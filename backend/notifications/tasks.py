from celery import shared_task
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_notification_event_task(self, notification_id, event_type):
    """
    Celery task to process notification events and send them to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        # Dynamically import the Notification model
        from notifications.models import Notification

        if event_type == 'deleted':
            # Prepare the message for deletion event
            message = {
                "notification_id": notification_id,
                "action": "deleted"
            }
        else:
            # Prepare the message for created or updated event
            notification = Notification.objects.get(id=notification_id)
            message = {
                "notification_id": notification.id,
                "sender_id": str(notification.sender.id),
                "receiver_id": str(notification.receiver.id),
                "notification_type": notification.notification_type,
                "text": notification.text,
                "created_at": str(notification.created_at),
                "event": event_type,
            }

        # Send the message to the Kafka topic for notification events
        kafka_topic = 'NOTIFICATIONS_EVENTS'
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for notification {event_type}: {message}")

    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)
    finally:
        producer.close()  # Ensure that the producer is properly closed
