# backend/kafka_app/tasks/album_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from kafka_app.constants import ALBUM_EVENTS, ALBUM_CREATED, ALBUM_UPDATED, ALBUM_DELETED, PHOTO_EVENTS

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
        event_type (str): Type of event to be processed (e.g., ALBUM_CREATED, ALBUM_UPDATED, ALBUM_DELETED).

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
            'event_type': event_type,         # e.g., ALBUM_CREATED
            'model_name': 'Album',            # Name of the model
            'id': str(album.id),              # UUID as string
            'data': _get_album_data(album),   # Event-specific data
        }

        # Send message to Kafka using KafkaService
        kafka_topic_key = ALBUM_EVENTS  # Use constant from constants.py
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
    Celery task to process photo events and send them to Kafka.
    """
    try:
        # Your logic to handle photo events
        message = {
            'event_type': event_type,
            'photo_id': str(photo_id),
            # Add more relevant fields
        }
        KafkaService().send_message(PHOTO_EVENTS, message)
        logger.info(f"Processed photo event {event_type} for photo ID {photo_id}")
    except Exception as e:
        logger.error(f"Error processing photo event {event_type} for photo ID {photo_id}: {e}")
        self.retry(exc=e)
