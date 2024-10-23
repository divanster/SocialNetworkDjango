# backend/stories/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
from .models import Story
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_story_event_to_kafka(self, story_id, event_type):
    """
    Celery task to send story events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
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
                "user_username": story.user_username,
                "content": story.content,
                "media_type": story.media_type,
                "media_url": story.media_url,
                "is_active": story.is_active,
                "created_at": str(story.created_at),
                "event": event_type,
            }

        # Send the constructed message to the STORY_EVENTS Kafka topic
        kafka_topic = settings.KAFKA_TOPICS.get('STORY_EVENTS', 'default-story-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for story event {event_type}: {message}")

    except Story.DoesNotExist:
        logger.error(f"Story with ID {story_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)  # Retry the task in case of failure
    finally:
        producer.close()  # Properly close the producer to ensure no open connections
