# backend/stories/signals.py

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.choices import VisibilityChoices
from stories.models import Story
from kafka_app.tasks.stories_tasks import send_story_event_to_kafka
from core.signals import soft_delete, restore  # Import custom signals

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from utils.group_names import get_user_group_name  # Import utility function

logger = logging.getLogger(__name__)


# ===========================
# Story Signals
# ===========================

@receiver(post_save, sender=Story)
def story_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler for Story model. It triggers a Celery task when a story is created or updated,
    and sends relevant event details to Kafka and WebSocket groups based on visibility.

    Args:
        sender (Model): The model class (Story).
        instance (Story): The actual instance being saved.
        created (bool): A boolean indicating if the instance is being created.
        **kwargs: Additional keyword arguments.
    """
    event_type = 'created' if created else 'updated'

    try:
        # Respect the visibility setting
        if instance.visibility == VisibilityChoices.PRIVATE:
            logger.info(f"[SIGNAL] Story {instance.pk} is private. No task triggered.")
            return

        # Trigger Celery task for story creation or update
        send_story_event_to_kafka.delay(str(instance.pk), event_type)
        logger.info(
            f"[SIGNAL] Triggered Celery task for story {event_type} with ID {instance.pk}"
        )

        # Send WebSocket notification
        user_group_name = get_user_group_name(
            instance.user.id)  # Assuming Story has a user field
        channel_layer = get_channel_layer()
        message = f"Your story has been {event_type}."
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'story_notification',
                'message': message,
                'event': event_type,
                'story_id': str(instance.id),
                'user_id': str(instance.user.id),
                'username': instance.user.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for story {event_type} with ID {instance.pk}"
        )

    except Exception as e:
        logger.error(f"Error in story_created_or_updated signal: {e}")


@receiver(soft_delete, sender=Story)
def story_soft_deleted(sender, instance, **kwargs):
    """
    Custom signal handler to process soft deletion of Story.
    Triggers a Celery task and sends WebSocket notifications.

    Args:
        sender (Model): The model class (Story).
        instance (Story): The instance being soft-deleted.
        **kwargs: Additional keyword arguments.
    """
    try:
        # Trigger Celery task to handle the story soft deletion event
        send_story_event_to_kafka.delay(str(instance.pk), 'soft_deleted')
        logger.info(
            f"[SIGNAL] Triggered Celery task for story soft deletion with ID {instance.pk}"
        )

        # Send WebSocket notification for story soft deletion
        user_group_name = get_user_group_name(
            instance.user.id)  # Assuming Story has a user field
        channel_layer = get_channel_layer()
        message = f"Your story has been soft-deleted."
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'story_notification',
                'message': message,
                'event': 'soft_deleted',
                'story_id': str(instance.id),
                'user_id': str(instance.user.id),
                'username': instance.user.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for story soft deletion with ID {instance.pk}"
        )

    except Exception as e:
        logger.error(f"Error in story_soft_deleted signal: {e}")


@receiver(restore, sender=Story)
def story_restored(sender, instance, **kwargs):
    """
    Custom signal handler to process restoration of a soft-deleted Story.
    Triggers a Celery task and sends WebSocket notifications.

    Args:
        sender (Model): The model class (Story).
        instance (Story): The instance being restored.
        **kwargs: Additional keyword arguments.
    """
    try:
        # Trigger Celery task to handle the story restoration event
        send_story_event_to_kafka.delay(str(instance.pk), 'restored')
        logger.info(
            f"[SIGNAL] Triggered Celery task for story restoration with ID {instance.pk}"
        )

        # Send WebSocket notification for story restoration
        user_group_name = get_user_group_name(
            instance.user.id)  # Assuming Story has a user field
        channel_layer = get_channel_layer()
        message = f"Your story has been restored."
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'story_notification',
                'message': message,
                'event': 'restored',
                'story_id': str(instance.id),
                'user_id': str(instance.user.id),
                'username': instance.user.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for story restoration with ID {instance.pk}"
        )

    except Exception as e:
        logger.error(f"Error in story_restored signal: {e}")
