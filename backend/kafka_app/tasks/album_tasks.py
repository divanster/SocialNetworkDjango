# backend/kafka_app/tasks/album_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from core.choices import VisibilityChoices
from albums.models import Album, Photo  # Ensure correct model imports

logger = logging.getLogger(__name__)


def _get_album_data(album):
    """
    Extract relevant data from the album instance.
    """
    return {
        'id': str(album.id),  # Include 'id' within 'data'
        'title': album.title,
        'description': album.description,
        'tagged_user_ids': [str(tagged_user.id) for tagged_user in album.tags.all()],
        'visibility': album.visibility,
        'user_id': str(album.user.id),
        # Add other relevant fields as needed
    }


def _get_photo_data(photo):
    """
    Extract relevant data from the photo instance.
    """
    return {
        'id': str(photo.id),  # Include 'id' within 'data'
        'album_id': str(photo.album.id) if photo.album else None,
        'description': photo.description,
        'tagged_user_ids': [str(tagged_user.id) for tagged_user in photo.tags.all()],
        'visibility': photo.album.visibility if photo.album else None,
        'user_id': str(photo.album.user.id) if photo.album else None,
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_album_event_task(self, album_id, event_type):
    """
    Celery task to process album events and send messages to Kafka.

    Args:
        self: Celery task instance.
        album_id (str): The ID of the album.
        event_type (str): Type of event to be processed (e.g., "created", "updated", "deleted").

    Returns:
        None
    """
    try:
        album = Album.objects.get(pk=album_id)

        # Respect visibility when constructing the Kafka message
        if album.visibility == VisibilityChoices.PRIVATE:
            logger.info(f"[TASK] Skipping Kafka message for private album with ID {album_id}")
            return

        # Construct the standardized Kafka message
        message = {
            'app': album._meta.app_label,     # e.g., 'albums'
            'event_type': event_type,         # e.g., 'created'
            'model_name': 'Album',            # Name of the model
            'id': str(album.id),              # UUID as string
            'data': _get_album_data(album),   # Event-specific data
        }

        # Send message to Kafka using KafkaService
        kafka_topic_key = 'ALBUM_EVENTS'  # Ensure this key exists in settings.KAFKA_TOPICS
        KafkaService().send_message(kafka_topic_key, message)  # Pass the key directly
        logger.info(f"[TASK] Successfully sent Kafka message for album event '{event_type}': {message}")

    except Album.DoesNotExist:
        logger.error(f"[TASK] Album with ID {album_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout occurred while processing album {album_id} for event {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[TASK] Unexpected error occurred while sending Kafka message for album {album_id}: {e}")
        self.retry(exc=e, countdown=60)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_photo_event_task(self, photo_id, event_type):
    """
    Celery task to process photo events and send messages to Kafka.

    Args:
        self: Celery task instance.
        photo_id (str): The ID of the photo.
        event_type (str): Type of event to be processed (e.g., "created", "updated", "deleted").

    Returns:
        None
    """
    try:
        photo = Photo.objects.get(pk=photo_id)

        # Respect visibility of the parent album when constructing the Kafka message
        if photo.album.visibility == VisibilityChoices.PRIVATE:
            logger.info(f"[TASK] Skipping Kafka message for photo in private album with ID {photo_id}")
            return

        # Construct the standardized Kafka message
        message = {
            'app': photo.album._meta.app_label,  # e.g., 'albums'
            'event_type': event_type,             # e.g., 'created'
            'model_name': 'Photo',                # Name of the model
            'id': str(photo.id),                  # UUID as string
            'data': _get_photo_data(photo),       # Event-specific data
        }

        # Send message to Kafka using KafkaService
        kafka_topic_key = 'PHOTO_EVENTS'  # Ensure this key exists in settings.KAFKA_TOPICS
        KafkaService().send_message(kafka_topic_key, message)  # Pass the key directly
        logger.info(f"[TASK] Successfully sent Kafka message for photo event '{event_type}': {message}")

    except Photo.DoesNotExist:
        logger.error(f"[TASK] Photo with ID {photo_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout occurred while processing photo {photo_id} for event {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[TASK] Unexpected error occurred while sending Kafka message for photo {photo_id}: {e}")
        self.retry(exc=e, countdown=60)
