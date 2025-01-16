# backend/kafka_app/tasks/stories_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from kafka_app.constants import STORY_EVENTS, STORY_SHARED  # Import constants
from stories.models import Story  # Ensure correct model import

logger = logging.getLogger(__name__)


def _get_story_data(story):
    """
    Extract relevant data from the story instance.
    """
    return {
        'id': str(story.id),              # Include 'id' within 'data'
        'title': story.title,
        'content': story.content,
        'user_id': str(story.user.id),
        'username': story.user.username,
        'visibility': story.visibility,
        'created_at': story.created_at.isoformat(),
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def send_story_shared_event_task(self, story_id, event_type):
    """
    Celery task to send story events to Kafka.
    """
    try:
        story = Story.objects.get(pk=story_id)

        # Construct the standardized Kafka message
        specific_event_type = f"story_{event_type}"  # e.g., 'story_shared'
        message = {
            'app': story._meta.app_label,       # e.g., 'stories'
            'event_type': specific_event_type,  # e.g., 'story_shared'
            'model_name': 'Story',              # Name of the model
            'id': str(story.id),                # UUID as string
            'data': _get_story_data(story),     # Event-specific data
        }

        # Send message to Kafka using KafkaService
        kafka_topic_key = STORY_EVENTS          # Use constant
        KafkaService().send_message(kafka_topic_key, message)  # Pass the key directly
        logger.info(f"[TASK] Successfully sent Kafka message for story event '{specific_event_type}': {message}")

    except Story.DoesNotExist:
        logger.error(f"[TASK] Story with ID {story_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout error while sending story '{event_type}': {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[TASK] Error sending Kafka message for story '{story_id}': {e}")
        self.retry(exc=e, countdown=60)
