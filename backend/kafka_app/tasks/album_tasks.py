# backend/kafka_app/tasks/album_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient
from core.choices import VisibilityChoices

logger = logging.getLogger(__name__)


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
        from albums.models import Album  # Local import to avoid circular imports
        producer = KafkaProducerClient()

        # Fetching the album by ID using Django ORM
        album = Album.objects.get(pk=album_id)

        # Respect visibility when constructing the Kafka message
        if album.visibility == VisibilityChoices.PRIVATE:
            # If it's private, don't send a Kafka event
            logger.info(f"[TASK] Skipping Kafka message for private album with ID {album_id}")
            return

        # Use reverse relation to get tagged users
        tagged_user_ids = [tagged_item.tagged_user_id for tagged_item in album.tags.all()]

        # Constructing the message for Kafka
        message = {
            'event': event_type,
            'album': str(album.pk),
            'title': album.title,
            'description': album.description,
            'tagged_user_ids': tagged_user_ids,
            'visibility': album.visibility,
            'user': str(album.user.pk)
        }

        # Send message to Kafka if visibility is public or friends
        if album.visibility in [VisibilityChoices.PUBLIC, VisibilityChoices.FRIENDS]:
            kafka_topic = settings.KAFKA_TOPICS.get('ALBUM_EVENTS', 'album-events')
            producer.send_message(kafka_topic, message)
            logger.info(f"[TASK] Successfully sent Kafka message for album event {event_type}: {message}")

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
        from albums.models import Photo  # Local import to avoid circular imports
        producer = KafkaProducerClient()

        # Fetching the photo by ID using Django ORM
        photo = Photo.objects.get(pk=photo_id)

        # Respect visibility of the parent album when constructing the Kafka message
        if photo.album.visibility == VisibilityChoices.PRIVATE:
            # If the album is private, don't send a Kafka event for the photo
            logger.info(f"[TASK] Skipping Kafka message for photo in private album with ID {photo_id}")
            return

        # Use reverse relation to get tagged users
        tagged_user_ids = [tagged_item.tagged_user_id for tagged_item in photo.tags.all()]

        # Constructing the message for Kafka
        message = {
            'event': event_type,
            'photo': str(photo.pk),
            'album': str(photo.album.pk) if photo.album else None,
            'description': photo.description,
            'tagged_user_ids': tagged_user_ids,
            'visibility': photo.album.visibility,
            'user': str(photo.album.user.pk)
        }

        # Send message to Kafka if visibility is public or friends
        if photo.album.visibility in [VisibilityChoices.PUBLIC, VisibilityChoices.FRIENDS]:
            kafka_topic = settings.KAFKA_TOPICS.get('PHOTO_EVENTS', 'photo-events')
            producer.send_message(kafka_topic, message)
            logger.info(f"[TASK] Successfully sent Kafka message for photo event {event_type}: {message}")

    except Photo.DoesNotExist:
        logger.error(f"[TASK] Photo with ID {photo_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout occurred while processing photo {photo_id} for event {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[TASK] Unexpected error occurred while sending Kafka message for photo {photo_id}: {e}")
        self.retry(exc=e, countdown=60)
