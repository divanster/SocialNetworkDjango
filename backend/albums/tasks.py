# backend/albums/tasks.py

from celery import shared_task
from kafka.errors import KafkaTimeoutError
from kafka_app.producer import KafkaProducerClient
from .models import Album, Photo
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def process_album_event_task(self, album_id, event_type):
    producer = KafkaProducerClient()
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

        # Send message to Kafka
        producer.send_message('ALBUM_EVENTS', message)
        logger.info(f"[TASK] Sent Kafka message for album {event_type}: {message}")

    except Album.DoesNotExist:
        logger.error(f"[TASK] Album with ID {album_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout: {e}")
        self.retry(exc=e,
                   countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[TASK] Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=5)
def process_photo_event_task(self, photo_id, event_type):
    producer = KafkaProducerClient()
    try:
        photo = Photo.objects.get(id=photo_id)
        message = {
            'event': event_type,
            'photo_id': str(photo.id),
            'album_id': str(photo.album.id),
            'description': photo.description,
            'image_path': photo.image.url,
        }

        # Send message to Kafka
        producer.send_message('PHOTO_EVENTS', message)
        logger.info(f"[TASK] Sent Kafka message for photo {event_type}: {message}")

    except Photo.DoesNotExist:
        logger.error(f"[TASK] Photo with ID {photo_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout: {e}")
        self.retry(exc=e,
                   countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"[TASK] Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=5)
def process_new_album(self, album_id):
    """
    Celery task to process a newly created album.
    This could be used to send notifications, perform analytics, or any other async processing.
    """
    try:
        album = Album.objects.get(id=album_id)

        # Perform post-processing tasks, e.g., analytics or notifications
        logger.info(
            f"[TASK] Processing new album with ID: {album_id} - Title: {album.title}")

        # Example: send_notification_to_followers(album_id)
        # analytics.process_album_created(album)

    except Album.DoesNotExist:
        logger.error(f"[TASK] Album with ID {album_id} does not exist.")
    except Exception as e:
        logger.error(f"[TASK] Error processing album with ID {album_id}: {e}")
        self.retry(exc=e, countdown=60 * (
                    2 ** self.request.retries))  # Exponential backoff retry
