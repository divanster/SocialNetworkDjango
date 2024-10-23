# backend/stories/tasks.py
from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from django.conf import settings
from .models import Story
import logging
import json

logger = logging.getLogger(__name__)

@shared_task
def send_story_event_to_kafka(story_id, event_type):
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "story_id": story_id,
                "event": "deleted"
            }
        else:
            story = Story.objects.using('stories_db').get(id=story_id)
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

        producer.send_message(settings.KAFKA_TOPICS['STORY_EVENTS'], message)
        logger.info(f"Sent Kafka message for story event {event_type}: {message}")
    except Story.DoesNotExist:
        logger.error(f"Story with ID {story_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
