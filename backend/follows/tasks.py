from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_follow_event_task(self, follow_id, event_type):
    """
    Celery task to process follow events and send them to Kafka.

    This function attempts to send information about a follow event (created or deleted)
    to a Kafka topic using a Kafka producer. In case of failure, it retries the operation.

    Args:
        follow_id (int): ID of the follow event.
        event_type (str): Type of the event, either 'created' or 'deleted'.

    Raises:
        self.retry: Retries the task in case of an exception.
    """
    from .models import Follow  # Move model import inside the function to avoid AppRegistryNotReady error
    producer = KafkaProducerClient()

    try:
        # Construct the message based on the event type
        if event_type == 'deleted':
            message = {
                "follow_id": follow_id,
                "action": "deleted"
            }
        else:
            follow = Follow.objects.get(id=follow_id)
            message = {
                "follow_id": follow.id,
                "follower_id": follow.follower.id,
                "follower_username": follow.follower.username,
                "followed_id": follow.followed.id,
                "followed_username": follow.followed.username,
                "created_at": str(follow.created_at),
                "event": event_type
            }

        # Get Kafka topic from settings for better flexibility
        kafka_topic = settings.KAFKA_TOPICS.get('FOLLOW_EVENTS', 'default-follow-topic')

        # Send message to Kafka
        producer.send_message(kafka_topic, message)
        logger.info(f"[KAFKA] Successfully sent follow {event_type} event to topic '{kafka_topic}': {message}")

        # Notify users via WebSocket groups
        send_websocket_notifications(message)

    except Follow.DoesNotExist:
        logger.error(f"[KAFKA] Follow with ID {follow_id} does not exist. Cannot send {event_type} event.")
    except Exception as e:
        logger.error(f"[KAFKA] Error sending follow {event_type} event to Kafka for follow ID {follow_id}: {e}")
        # Retry the task in case of failure, with exponential backoff
        raise self.retry(exc=e, countdown=60)


def send_websocket_notifications(message):
    """
    Sends WebSocket notifications to the follower and the user being followed.
    """
    try:
        from websocket.consumers import GeneralKafkaConsumer  # Import inside function to avoid circular dependencies
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        # Generate group names for follower and followed user
        follower_group_name = GeneralKafkaConsumer.generate_group_name(message['follower_id'])
        followed_group_name = GeneralKafkaConsumer.generate_group_name(message['followed_id'])

        # Notify the follower
        async_to_sync(channel_layer.group_send)(
            follower_group_name,
            {
                'type': 'user.notification',
                'message': f"New follow event: {message}"
            }
        )

        # Notify the user being followed
        async_to_sync(channel_layer.group_send)(
            followed_group_name,
            {
                'type': 'user.notification',
                'message': f"New follow event: {message}"
            }
        )

        logger.info(f"WebSocket notifications sent for follow event: {message}")

    except Exception as e:
        logger.error(f"Error sending WebSocket notifications for follow event: {e}")
