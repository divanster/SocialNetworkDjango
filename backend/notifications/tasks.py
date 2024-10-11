# backend/notifications/tasks.py

from celery import shared_task

from kafka_app.consumer import KafkaConsumerClient
from kafka_app.producer import KafkaProducerClient
from .models import Notification
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_notification_event_to_kafka(notification_id, event_type):
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
                "user_id": notification.user_id,
                "message": notification.message,
                "created_at": str(notification.created_at),
                "event": event_type,
            }

        producer.send_message('NOTIFICATIONS_EVENTS', message)
        logger.info(f"Sent Kafka message for notification {event_type}: {message}")
    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")

@shared_task
def consume_notification_events():
    consumer = KafkaConsumerClient('NOTIFICATIONS_EVENTS')
    for message in consumer.consume_messages():
        try:
            # Add processing logic here for received notification messages
            logger.info(f"Processed notification event: {message}")
        except Exception as e:
            logger.error(f"Error processing notification event: {e}")
