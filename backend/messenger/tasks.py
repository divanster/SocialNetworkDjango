from celery import shared_task
from django.conf import settings
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def process_message_event_task(self, message_id, event_type):
    """
    Celery task to process message events and send them to Kafka.
    """
    # Import the Message model inside the function to prevent AppRegistryNotReady errors
    from .models import Message

    producer = KafkaProducerClient()

    try:
        # Construct the Kafka message based on the event type
        if event_type == 'deleted':
            message = {
                "message_id": message_id,
                "action": "deleted"
            }
        else:
            # Fetch the message instance to create the message payload
            message_instance = Message.objects.get(id=message_id)
            message = {
                "message_id": str(message_instance.id),
                "sender_id": str(message_instance.sender.id),
                "sender_username": message_instance.sender.username,
                "receiver_id": str(message_instance.receiver.id),
                "receiver_username": message_instance.receiver.username,
                "content": message_instance.content,
                "timestamp": str(message_instance.timestamp),
                "event": event_type
            }

        # Get Kafka topic from settings
        kafka_topic = settings.KAFKA_TOPICS.get('MESSENGER_EVENTS', 'default-messenger-topic')
        producer.send_message(kafka_topic, message)

        logger.info(f"Sent Kafka message for message {event_type}: {message}")

        # Notify users via WebSocket
        send_websocket_notifications(message)

    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    finally:
        producer.close()  # Ensure the producer is properly closed


def send_websocket_notifications(message):
    """
    Sends WebSocket notifications to the involved users (sender and receiver).
    """
    try:
        from websocket.consumers import GeneralKafkaConsumer  # Import inside function to avoid circular dependencies
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        # Generate group names for sender and receiver
        sender_group_name = GeneralKafkaConsumer.generate_group_name(message['sender_id'])
        receiver_group_name = GeneralKafkaConsumer.generate_group_name(message['receiver_id'])

        # Send WebSocket notifications to both sender and receiver
        async_to_sync(channel_layer.group_send)(
            sender_group_name,
            {
                'type': 'message_notification',
                'message': f"Message {message['event']}: {message}"
            }
        )

        async_to_sync(channel_layer.group_send)(
            receiver_group_name,
            {
                'type': 'message_notification',
                'message': f"Message {message['event']}: {message}"
            }
        )

        logger.info(f"WebSocket notifications sent for message event: {message}")

    except Exception as e:
        logger.error(f"Error sending WebSocket notifications for message event: {e}")
