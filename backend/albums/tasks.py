from celery import shared_task
from kafka.errors import KafkaTimeoutError
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5)
def process_album_event_task(self, album_id, event_type):
    from .album_models import Album  # Correct import for the split model
    producer = KafkaProducerClient()
    try:
        album = Album.objects.get(pk=album_id)  # Use MongoEngine querying
        tagged_user_ids = [str(tag.user_id) for tag in album.tags]  # Adjust for MongoEngine field

        message = {
            'event': event_type,
            'album': str(album.pk),
            'title': album.title,
            'description': album.description,
            'tagged_user_ids': tagged_user_ids,
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
    from .photo_models import Photo  # Correct import for the split model
    producer = KafkaProducerClient()
    try:
        photo = Photo.objects.get(pk=photo_id)  # Use MongoEngine querying
        message = {
            'event': event_type,
            'photo_id': str(photo.pk),
            'album_id': str(photo.album.pk),  # Access album using MongoEngine reference field
            'description': photo.description,
            'image_path': str(photo.image),  # Assuming the `image` field is a reference in GridFS or similar
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
    from .album_models import Album  # Correct import for the split model
    """
    Celery task to process a newly created album.
    This could be used to send notifications, perform analytics, or any other async processing.
    """
    try:
        album = Album.objects.get(pk=album_id)  # Use MongoEngine querying

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
