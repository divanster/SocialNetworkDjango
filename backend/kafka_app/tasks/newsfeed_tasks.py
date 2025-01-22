import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from kafka_app.tasks.base_task import BaseTask
from kafka_app.services import KafkaService
from kafka_app.constants import (
    NEWSFEED_EVENTS,
    EVENT_DELETED,
    POST_CREATED,
    POST_UPDATED,
    POST_DELETED,
    COMMENT_CREATED,
    REACTION_CREATED,
    ALBUM_CREATED,
    STORY_EVENTS,  # Updated here
)
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
    """
    try:
        # Log the event type and object ID for debugging purposes
        logger.debug(f"Received event_type: {event_type} for {model_name} with object_id: {object_id}")

        # Validate event_type
        if not event_type:
            logger.error(f"Invalid event_type received for {model_name} with ID {object_id}")
            return  # Early exit if event_type is None

        # Map the model_name to the actual model
        model = MODEL_MAP.get(model_name)
        if not model:
            raise ValueError(f"Unknown model: {model_name}")

        if event_type == EVENT_DELETED:
            # Create a message for deleted events with just the object ID and event type
            specific_event_type = f"{model_name.lower()}_deleted"  # e.g., 'post_deleted'
            message = {
                'app': model._meta.app_label,
                'event_type': specific_event_type,  # e.g., 'post_deleted'
                'model_name': model_name,
                'id': str(object_id),
                'data': {}  # Empty data for deleted events
            }
        else:
            # For created or updated events, fetch the instance and construct the message
            try:
                instance = model.objects.get(id=object_id)
            except model.DoesNotExist:
                logger.error(f"{model_name} with ID {object_id} does not exist.")
                return  # Exit if the instance is not found

            # Construct the specific event type
            specific_event_type = f"{model_name.lower()}_{event_type}"  # e.g., 'post_created'
            message = {
                'app': model._meta.app_label,
                'event_type': specific_event_type,  # e.g., 'post_created'
                'model_name': model_name,
                'id': str(instance.id),
                'data': _get_instance_data(instance),
            }

        # Log the constructed message for debugging
        logger.debug(f"Constructed Kafka message: {message}")

        # Send the message to Kafka
        kafka_topic_key = NEWSFEED_EVENTS
        KafkaService().send_message(kafka_topic_key, message)
        logger.info(f"Successfully sent Kafka message for {model_name} {event_type}: {message}")

    except ValueError as e:
        logger.error(f"ValueError: {e}")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending newsfeed {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Unexpected error while sending Kafka message for {model_name} {event_type}: {e}")
        self.retry(exc=e, countdown=60)
