# backend/kafka_app/tasks/newsfeed_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError

from kafka_app.services import KafkaService
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from stories.models import Story  # Ensure these models are correctly defined in their apps

logger = logging.getLogger(__name__)

MODEL_MAP = {
    'Post': Post,
    'Comment': Comment,
    'Reaction': Reaction,
    'Album': Album,
    'Story': Story,
}

def _get_instance_data(instance):
    """
    Extract data from an instance to send in the Kafka message.
    Adjust this function to handle specific fields per model.
    """
    data = {}
    if hasattr(instance, 'id'):
        data['id'] = str(instance.id)  # Ensure 'id' is within 'data'
    if hasattr(instance, 'content'):
        data['content'] = instance.content
    if hasattr(instance, 'created_at'):
        data['created_at'] = instance.created_at.isoformat()
    if hasattr(instance, 'author_id'):
        data['author_id'] = str(instance.author_id)
    if hasattr(instance, 'author_username'):
        data['author_username'] = instance.author_username
    if hasattr(instance, 'title'):
        data['title'] = instance.title
    if hasattr(instance, 'visibility'):
        data['visibility'] = instance.visibility
    # Add more fields as needed per model
    return data

@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def send_newsfeed_event_task(self, object_id, event_type, model_name):
    """
    Celery task to send various newsfeed model events to Kafka.

    Args:
        self: Celery task instance.
        object_id (UUID): The ID of the object.
        event_type (str): Type of event (e.g., "created", "updated", "deleted").
        model_name (str): The name of the model (e.g., "Post", "Comment").

    Returns:
        None
    """
    try:
        model = MODEL_MAP.get(model_name)
        if not model:
            raise ValueError(f"Unknown model: {model_name}")

        if event_type == 'deleted':
            # Create a message for deleted events with just the object ID and event type
            message = {
                'app': model._meta.app_label,
                'event_type': event_type,
                'model_name': model_name,
                'id': str(object_id),
                'data': {}  # Empty data for deleted events
            }
        else:
            # Fetch the instance from the database for created or updated events
            instance = model.objects.get(id=object_id)
            message = {
                'app': model._meta.app_label,
                'event_type': event_type,
                'model_name': model_name,
                'id': str(instance.id),
                'data': _get_instance_data(instance),
            }

        # Send the constructed message to the Kafka topic using KafkaService
        kafka_topic_key = 'NEWSFEED_EVENTS'  # Ensure this key exists in settings.KAFKA_TOPICS
        KafkaService().send_message(kafka_topic_key, message)  # Pass the key
        logger.info(f"Sent Kafka message for {model_name} {event_type}: {message}")

    except model.DoesNotExist:
        logger.error(f"{model_name} with ID {object_id} does not exist.")
    except ValueError as e:
        logger.error(f"ValueError: {e}")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending newsfeed {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
