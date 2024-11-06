from celery import shared_task
from django.conf import settings
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def process_notification_event_task(self, notification_id, event_type):
    """
    Celery task to process notification events and send them to Kafka and WebSocket.
    """
    # Import the Notification model inside the function to prevent AppRegistryNotReady errors
    from .models import Notification

    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "notification_id": notification_id,
                "action": "deleted"
            }
        else:
            # Fetch the notification instance to create the message payload
            notification_instance = Notification.objects.get(id=notification_id)
            message = {
                "notification_id": str(notification_instance.id),
                "recipient_id": str(notification_instance.recipient.id),
                "recipient_username": notification_instance.recipient.username,
                "sender_id": str(notification_instance.sender.id) if notification_instance.sender else None,
                "sender_username": notification_instance.sender.username if notification_instance.sender else None,
                "notification_type": notification_instance.notification_type,
                "text": notification_instance.text,
                "timestamp": str(notification_instance.timestamp),
                "event": event_type
            }

        # Get Kafka topic from settings
        kafka_topic = settings.KAFKA_TOPICS.get('NOTIFICATION_EVENTS', 'default-notification-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for notification {event_type}: {message}")

        # Notify user via WebSocket
        send_websocket_notification(message)

    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message for notification event: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    finally:
        producer.close()  # Ensure the producer is properly closed


def send_websocket_notification(message):
    """
    Sends WebSocket notification to the involved user (e.g., the recipient of the notification).
    """
    try:
        from websocket.consumers import GeneralKafkaConsumer  # Import to avoid circular dependencies
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        if 'recipient_id' in message:
            recipient_id = message['recipient_id']
            user_group_name = GeneralKafkaConsumer.generate_group_name(recipient_id)

            # Notify the recipient of the notification event
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'notification_message',
                    'message': f"Notification {message['event']}: {message}"
                }
            )
            logger.info(f"Real-time WebSocket notification sent for notification event '{message['event']}' with ID {message['notification_id']}")

    except Exception as e:
        logger.error(f"Error sending WebSocket notification for notification event: {e}")
