from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
import logging
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

@shared_task
def send_tagging_event_to_kafka(tagged_item_id, event_type):
    """
    Celery task to send tagging events to Kafka and notify the user via WebSocket.

    Args:
        tagged_item_id (int): The ID of the tagged item.
        event_type (str): The type of event to process (e.g., 'created', 'deleted').
    """
    from .models import TaggedItem  # Lazy import to prevent circular dependencies
    producer = KafkaProducerClient()

    try:
        # Construct the message for Kafka
        if event_type == 'deleted':
            message = {
                "tagged_item_id": tagged_item_id,
                "event": "deleted"
            }
        else:
            # Fetch the TaggedItem instance from the database
            tagged_item = TaggedItem.objects.get(id=tagged_item_id)
            message = {
                "tagged_item_id": tagged_item.id,
                "tagged_user_id": tagged_item.tagged_user.id,
                "content_type": str(tagged_item.content_type),
                "object_id": tagged_item.object_id,
                "tagged_by_id": tagged_item.tagged_by.id,
                "created_at": str(tagged_item.created_at),
                "event": event_type,
            }

        # Send message to Kafka
        kafka_topic = settings.KAFKA_TOPICS.get('TAGGING_EVENTS', 'default-tagging-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for tagging event {event_type}: {message}")

        # If it's not a deletion, trigger WebSocket notification
        if event_type != 'deleted':
            send_websocket_notification_for_tagging(tagged_item, event_type)

    except TaggedItem.DoesNotExist:
        logger.error(f"TaggedItem with ID {tagged_item_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
    finally:
        producer.close()  # Ensure producer is closed to free resources


def send_websocket_notification_for_tagging(tagged_item, event_type):
    """
    Send real-time WebSocket notification for a tagging event.

    Args:
        tagged_item (TaggedItem): The tagged item instance.
        event_type (str): The type of event to process (e.g., 'created', 'updated').
    """
    from websocket.consumers import GeneralKafkaConsumer  # Import here to avoid circular imports
    from channels.layers import get_channel_layer

    try:
        user_group_name = GeneralKafkaConsumer.generate_group_name(tagged_item.tagged_user.id)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'tag_notification',
                'message': f"You were tagged by {tagged_item.tagged_by.username} in a post."
            }
        )
        logger.info(f"Real-time WebSocket notification sent for tagging event '{event_type}' with ID {tagged_item.id}")

    except Exception as e:
        logger.error(f"Error sending WebSocket notification for tagging event: {e}")


@shared_task
def consume_tagging_events():
    """
    Celery task to consume tagging events from Kafka.
    """
    try:
        # Placeholder implementation, should be updated based on Kafka client
        logger.warning("The consume_tagging_events task is not implemented.")
    except Exception as e:
        logger.error(f"Error consuming tagging events: {e}")
