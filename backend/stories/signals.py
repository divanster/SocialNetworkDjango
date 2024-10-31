import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Story
from .tasks import send_story_event_to_kafka  # Import the Celery task

# Initialize logger
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Story)
def story_saved(sender, instance, created, **kwargs):
    """
    Signal to handle logic after a Story instance is saved.
    Logs whether the story was created or updated and sends an event to Kafka using a Celery task.
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

    except Exception as e:
        logger.error(f"Error in story_saved signal: {e}")


@receiver(post_delete, sender=Story)
def story_deleted(sender, instance, **kwargs):
    """
    Signal to handle logic after a Story instance is deleted.
    Logs the deletion of the story and sends an event to Kafka using a Celery task.
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

    except Exception as e:
        logger.error(f"Error in story_deleted signal: {e}")
