# backend/albums/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from .models import Album, Photo
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_album_event_to_kafka(album_id, event_type):
    """
    Celery task to send album events to Kafka.
    """
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

        producer.send_message('ALBUM_EVENTS', message)
        logger.info(f"Sent Kafka message for album {event_type}: {message}")
    except Album.DoesNotExist:
        logger.error(f"Album with ID {album_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


@shared_task
def send_photo_event_to_kafka(photo_id, event_type):
    """
    Celery task to send photo events to Kafka.
    """
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

        producer.send_message('PHOTO_EVENTS', message)
        logger.info(f"Sent Kafka message for photo {event_type}: {message}")
    except Photo.DoesNotExist:
        logger.error(f"Photo with ID {photo_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
