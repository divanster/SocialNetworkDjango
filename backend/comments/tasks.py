from celery import shared_task
from kafka.errors import KafkaTimeoutError
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def process_comment_event_task(self, comment_id, event_type):
    """
    Celery task to process comment events and send them to Kafka.

    Args:
        self (Celery task instance): Allows task retries and management.
        comment_id (str or UUID): The ID of the comment to be processed.
        event_type (str): The type of event to process (e.g., "created", "updated", "deleted").
    """
    # Import the model within the function to prevent AppRegistryNotReady errors
    from .models import Comment
    producer = KafkaProducerClient()

    try:
        # Construct the Kafka message based on event type
        if event_type == 'deleted':
            message = {
                "event": "deleted",
                "comment_id": str(comment_id),
            }
        else:
            # Retrieve the comment object from the database
            comment = Comment.objects.get(id=comment_id)

            # Create the message to be sent to Kafka
            message = {
                "event": event_type,
                "comment_id": str(comment.id),
                "content": comment.content,
                "user_id": str(comment.user.id),
                "user_username": comment.user.username,  # Including username for better identification
                "post_id": str(comment.post_id),
                "created_at": str(comment.created_at),
            }

        # Get Kafka topic for comment events from settings
        kafka_topic = settings.KAFKA_TOPICS.get('COMMENT_EVENTS', 'default-comment-topic')

        # Send the message to the Kafka topic for comments
        producer.send_message(kafka_topic, message)
        logger.info(f"[TASK] Sent Kafka message for comment {event_type}: {message}")

        # Notify user via WebSocket group
        send_websocket_notification(message['user_id'], f"New comment {event_type}: {message}")

    except Comment.DoesNotExist:
        logger.error(f"[TASK] Comment with ID {comment_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout: {e}")
        # Retry the task with exponential backoff
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    except Exception as e:
        logger.error(f"[TASK] Error sending Kafka message: {e}")
        # Retry the task in case of unexpected errors
        self.retry(exc=e, countdown=60)


def send_websocket_notification(user_id, message):
    """
    Sends a WebSocket notification to the group of the given user_id.
    """
    try:
        from websocket.consumers import GeneralKafkaConsumer  # Import locally to avoid circular import issues
        channel_layer = get_channel_layer()
        user_group_name = GeneralKafkaConsumer.generate_group_name(user_id)

        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'user.notification',
                'message': message
            }
        )
        logger.info(f"Sent WebSocket notification to user group {user_group_name} with message: {message}")
    except Exception as e:
        logger.error(f"Error sending WebSocket notification for user {user_id}: {e}")
