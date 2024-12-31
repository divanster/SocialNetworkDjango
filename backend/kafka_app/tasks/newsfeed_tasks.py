# backend/kafka_app/tasks/newsfeed_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


MODEL_MAP = {
    'Post': 'social.models.Post',
    'Comment': 'comments.models.Comment',
    'Reaction': 'reactions.models.Reaction',
    'Album': 'albums.models.Album',
    'Story': 'stories.models.Story',
}


def _dynamic_import(model_path):
    """
    Dynamically import a model class based on its full path.
    """
    components = model_path.split('.')
    module_path = '.'.join(components[:-1])
    model_name = components[-1]

    module = __import__(module_path, fromlist=[model_name])
    return getattr(module, model_name)


def _get_instance_data(instance):
    """
    Extract data from an instance to send in the Kafka message.
    Adjust this function to handle specific fields per model.
    """
    data = {}
    if hasattr(instance, 'content'):
        data['content'] = instance.content
    if hasattr(instance, 'created_at'):
        data['created_at'] = str(instance.created_at)
    if hasattr(instance, 'author_id'):
        data['author_id'] = instance.author_id
    if hasattr(instance, 'author_username'):
        data['author_username'] = instance.author_username
    if hasattr(instance, 'title'):
        data['title'] = instance.title

    # Add more fields as needed per model
    return data


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def send_newsfeed_event_task(self, object_id, event_type, model_name):
    """
    Celery task to send various newsfeed model events to Kafka.

    Args:
        self: Celery task instance.
        object_id (int): The ID of the object.
        event_type (str): Type of event (e.g., "created", "updated", "deleted").
        model_name (str): The name of the model (e.g., "Post", "Comment").

    Returns:
        None
    """
    try:
        producer = KafkaProducerClient()

        # Dynamically import the model
        model_path = MODEL_MAP.get(model_name)
        if not model_path:
            raise ValueError(f"Unknown model: {model_name}")

        model = _dynamic_import(model_path)

        if event_type == 'deleted':
            # Create a message for deleted events with just the object ID and event type
            message = {
                'id': object_id,
                'event_type': event_type,
                'model_name': model_name,
            }
        else:
            # Fetch the instance from the database for created or updated events
            instance = model.objects.get(id=object_id)
            message = {
                'id': instance.id,
                'event_type': event_type,
                'model_name': model_name,
                'data': _get_instance_data(instance),
            }

        # Send the constructed message to the NEWSFEED_EVENTS Kafka topic
        kafka_topic = settings.KAFKA_TOPICS.get('NEWSFEED_EVENTS', 'newsfeed-events')
        producer.send_message(kafka_topic, message)
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
