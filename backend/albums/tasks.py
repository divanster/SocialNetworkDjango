from celery import shared_task
from kafka.errors import KafkaTimeoutError
from kafka_app.producer import KafkaProducerClient
import logging

# Setting up the logger
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
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
    from albums.models import \
        Album  # Importing within the function to avoid circular imports
    producer = KafkaProducerClient()

    try:
        # Fetching the album by ID using Django ORM
        album = Album.objects.get(pk=album_id)

        # Extract tagged_user_ids from tags if it's not empty
        tagged_user_ids = [str(user_id) for user_id in album.tags]

        # Constructing the message for Kafka
        message = {
            'event': event_type,
            'album': str(album.pk),
            'title': album.title,
            'description': album.description,
            'tagged_user_ids': tagged_user_ids,
        }

        # Send message to Kafka
        producer.send_message('ALBUM_EVENTS', message)
        logger.info(
            f"[TASK] Successfully sent Kafka message for album event {event_type}: {message}")

    except Album.DoesNotExist:
        logger.error(f"[TASK] Album with ID {album_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(
            f"[TASK] Kafka timeout occurred while processing album {album_id} for event {event_type}: {e}")
        self.retry(exc=e,
                   countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(
            f"[TASK] Unexpected error occurred while sending Kafka message for album {album_id}: {e}")
        self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=5)
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
    from albums.models import \
        Photo  # Importing within the function to avoid circular imports
    producer = KafkaProducerClient()

    try:
        # Fetching the photo by ID using Django ORM
        photo = Photo.objects.get(pk=photo_id)

        # Constructing the message for Kafka
        message = {
            'event': event_type,
            'photo': str(photo.pk),
            'album': str(photo.album.pk) if photo.album else None,
            'description': photo.description,
            'tags': photo.tags,
        }

        # Send message to Kafka
        producer.send_message('PHOTO_EVENTS', message)
        logger.info(
            f"[TASK] Successfully sent Kafka message for photo event {event_type}: {message}")

    except Photo.DoesNotExist:
        logger.error(f"[TASK] Photo with ID {photo_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(
            f"[TASK] Kafka timeout occurred while processing photo {photo_id} for event {event_type}: {e}")
        self.retry(exc=e,
                   countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(
            f"[TASK] Unexpected error occurred while sending Kafka message for photo {photo_id}: {e}")
        self.retry(exc=e, countdown=60)
