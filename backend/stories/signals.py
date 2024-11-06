import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Story
from .tasks import send_story_event_to_kafka  # Import the Celery task
from websocket.consumers import \
    GeneralKafkaConsumer  # Import for generating group names

# Initialize logger
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Story)
def story_saved(sender, instance, created, **kwargs):
    """
    Signal to handle logic after a Story instance is saved.
    Logs whether the story was created or updated and sends an event to Kafka using a Celery task.
    Also sends WebSocket notification to the user.
    """
    event_type = 'created' if created else 'updated'

    try:
        # Fetching user username directly from the related User model
        user_username = instance.user.username

        # Log event details
        logger.info(
            f"Story {event_type} with ID: {instance.id}, User: {user_username}, "
            f"Content: {(instance.content[:30] + '...') if instance.content else 'No Content'}, "
            f"Media Type: {instance.media_type}"
        )

        # Trigger Celery task to send story event to Kafka
        send_story_event_to_kafka.delay(instance.id, event_type)

        # Send WebSocket notification
        channel_layer = get_channel_layer()
        user_group_name = GeneralKafkaConsumer.generate_group_name(instance.user.id)
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'story_message',
                'event': event_type,
                'story': str(instance.id),
                'content': instance.content,
                'media_type': instance.media_type,
            }
        )
        logger.info(
            f"Real-time update sent for story {event_type} event with ID {instance.id}")

    except Exception as e:
        logger.error(f"Error in story_saved signal: {e}")


@receiver(post_delete, sender=Story)
def story_deleted(sender, instance, **kwargs):
    """
    Signal to handle logic after a Story instance is deleted.
    Logs the deletion of the story and sends an event to Kafka using a Celery task.
    Also sends WebSocket notification to the user.
    """
    try:
        # Fetching user username directly from the related User model
        user_username = instance.user.username

        # Log delete details
        logger.info(
            f"Story deleted with ID: {instance.id}, User: {user_username}, "
            f"Content: {(instance.content[:30] + '...') if instance.content else 'No Content'}"
        )

        # Trigger Celery task to send story deleted event to Kafka
        send_story_event_to_kafka.delay(instance.id, 'deleted')

        # Send WebSocket notification
        channel_layer = get_channel_layer()
        user_group_name = GeneralKafkaConsumer.generate_group_name(instance.user.id)
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'story_message',
                'event': 'deleted',
                'story': str(instance.id),
                'content': instance.content,
                'media_type': instance.media_type,
            }
        )
        logger.info(f"Real-time delete notification sent for story ID {instance.id}")

    except Exception as e:
        logger.error(f"Error in story_deleted signal: {e}")
