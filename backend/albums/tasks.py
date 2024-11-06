from celery import shared_task
from kafka.errors import KafkaTimeoutError
from kafka_app.producer import KafkaProducerClient
import logging
from core.choices import VisibilityChoices
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Setting up the logger
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def process_album_event_task(self, album_id, event_type):
    """
    Celery task to process album events and send messages to Kafka.
    """
    from albums.models import Album  # Importing within the function to avoid circular imports
    from tagging.models import TaggedItem
    producer = KafkaProducerClient()

    try:
        # Fetching the album by ID using Django ORM
        album = Album.objects.get(pk=album_id)

        # Respect visibility when constructing the Kafka message
        if album.visibility == VisibilityChoices.PRIVATE:
            # If it's private, don't send a Kafka event
            logger.info(
                f"[TASK] Skipping Kafka message for private album with ID {album_id}")
            return

        # Extract tagged_user_ids from tags if they exist
        tagged_user_ids = [
            tagged_item.tagged_user_id for tagged_item in
            TaggedItem.objects.filter(content_object=album)
        ]

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
            producer.send_message('ALBUM_EVENTS', message)
            logger.info(
                f"[TASK] Successfully sent Kafka message for album event {event_type}: {message}")

            # Notify user via WebSocket group
            send_websocket_notification(album.user.pk, f"New album {event_type}: {message}")

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
    """
    from albums.models import Photo  # Importing within the function to avoid circular imports
    from tagging.models import TaggedItem
    producer = KafkaProducerClient()

    try:
        # Fetching the photo by ID using Django ORM
        photo = Photo.objects.get(pk=photo_id)

        # Respect visibility of the parent album when constructing the Kafka message
        if photo.album.visibility == VisibilityChoices.PRIVATE:
            logger.info(
                f"[TASK] Skipping Kafka message for photo in private album with ID {photo_id}")
            return

        # Extract tagged_user_ids from tags if they exist
        tagged_user_ids = [
            tagged_item.tagged_user_id for tagged_item in
            TaggedItem.objects.filter(content_object=photo)
        ]

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
            producer.send_message('PHOTO_EVENTS', message)
            logger.info(
                f"[TASK] Successfully sent Kafka message for photo event {event_type}: {message}")

            # Notify user via WebSocket group
            send_websocket_notification(photo.album.user.pk, f"New photo {event_type}: {message}")

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


def send_websocket_notification(user_id, message):
    """
    Sends a WebSocket notification to the group of the given user_id.
    """
    try:
        from websocket.consumers import GeneralKafkaConsumer  # Import locally to avoid circular import issues
        channel_layer = get_channel_layer()
        user_group_name = GeneralKafkaConsumer.generate_group_name(user_id)

        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'user.notification',
                'message': message
            }
        )
        logger.info(f"Sent WebSocket notification to user group {user_group_name} with message: {message}")
    except Exception as e:
        logger.error(f"Error sending WebSocket notification for user {user_id}: {e}")
