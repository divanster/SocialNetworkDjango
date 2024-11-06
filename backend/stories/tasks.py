from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
import logging
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_story_event_to_kafka(self, story_id, event_type):
    """
    Celery task to send story events to Kafka and notify users via WebSocket.

    Args:
        story_id (str): ID of the story.
        event_type (str): Type of event to be processed ('created', 'updated', 'deleted').

    Returns:
        None
    """
    producer = KafkaProducerClient()

    try:
        # Import the Story model to avoid circular dependencies
        from stories.models import Story

        if event_type == 'deleted':
            # Prepare the message for deleted story event
            message = {
                "story_id": story_id,
                "event": "deleted"
            }
        else:
            # Fetch the story instance from the database
            story = Story.objects.get(id=story_id)

            message = {
                "story_id": story.id,
                "user_id": story.user_id,
                "user_username": story.user.username,
                "content": story.content,
                "media_type": story.media_type,
                "media_url": story.media_url,
                "visibility": story.visibility,
                "is_active": story.is_active,
                "created_at": str(story.created_at),
                "event": event_type,
            }

        # Send the constructed message to the STORY_EVENTS Kafka topic
        kafka_topic = settings.KAFKA_TOPICS.get('STORY_EVENTS', 'default-story-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for story event '{event_type}' with message: {message}")

        # Trigger the WebSocket notification for the story event
        send_websocket_notification(story, event_type)

    except Story.DoesNotExist:
        logger.error(f"Story with ID '{story_id}' does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message for story ID '{story_id}': {e}")
        self.retry(exc=e)  # Retry the task in case of failure
    finally:
        producer.close()  # Properly close the producer to ensure no open connections


def send_websocket_notification(story, event_type):
    """
    Send real-time WebSocket notifications for a story event.

    Args:
        story (Story): The story instance.
        event_type (str): The type of the event ('created', 'updated', 'deleted').
    """
    from websocket.consumers import GeneralKafkaConsumer  # Import to avoid circular dependencies
    from channels.layers import get_channel_layer

    try:
        # WebSocket notification - Notify the user of the story event
        channel_layer = get_channel_layer()
        user_group_name = GeneralKafkaConsumer.generate_group_name(story.user_id)
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'story_message',
                'event': event_type,
                'story': str(story.id),
                'content': story.content,
                'media_type': story.media_type,
            }
        )
        logger.info(f"Real-time WebSocket notification sent for story event '{event_type}' with ID {story.id}")
    except Exception as e:
        logger.error(f"Error sending WebSocket notification for story ID '{story.id}': {e}")
