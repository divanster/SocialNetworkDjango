# backend/albums/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from .models import Album, Photo
from albums.utils import get_kafka_producer
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_album_event_to_kafka(self, album_id, event_type):
    producer = get_kafka_producer()

    try:
        album = Album.objects.get(id=album_id)
        tagged_user_ids = list(album.tags.values_list('tagged_user_id', flat=True))

        message = {
            'event': event_type,
            'album': str(album.id),
            'title': album.title,
            'description': album.description,
            'tagged_user_ids': [str(user_id) for user_id in tagged_user_ids],
        }

        producer.send_message('ALBUM_EVENTS', message)
        logger.info(f"[TASK] Sent Kafka message for album {event_type}: {message}")
    except Album.DoesNotExist:
        logger.error(f"[TASK] Album with ID {album_id} does not exist.")
    except Exception as e:
        logger.error(f"[TASK] Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_photo_event_to_kafka(self, photo_id, event_type):
    producer = get_kafka_producer()

    try:
        photo = Photo.objects.get(id=photo_id)

        message = {
            'event': event_type,
            'photo_id': str(photo.id),
            'album_id': str(photo.album.id),
            'description': photo.description,
            'image_path': photo.image.url,
        }

        producer.send_message('PHOTO_EVENTS', message)
        logger.info(f"[TASK] Sent Kafka message for photo {event_type}: {message}")
    except Photo.DoesNotExist:
        logger.error(f"[TASK] Photo with ID {photo_id} does not exist.")
    except Exception as e:
        logger.error(f"[TASK] Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)


@shared_task
def process_new_album(album_id):
    """
    Celery task to process a newly created album.
    """
    try:
        album = Album.objects.get(id=album_id)
        # Add any post-processing logic here (e.g., notifications, analytics)
        logger.info(f"Processing new album with ID: {album_id} - Title: {album.title}")
    except Album.DoesNotExist:
        logger.error(f"Album with ID {album_id} does not exist.")
    except Exception as e:
        logger.error(f"Error processing album with ID {album_id}: {e}")
