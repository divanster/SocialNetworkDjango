# backend/users/signals.py

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser, UserProfile
from kafka_app.tasks import process_user_event_task  # Import the Celery task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from utils.group_names import get_user_group_name  # New import

from core.signals import soft_delete, restore  # Import custom signals

from stories.models import Story
from kafka_app.tasks.stories_tasks import send_story_shared_event_task  # Import the Celery task

logger = logging.getLogger(__name__)


# ===========================
# CustomUser Signals
# ===========================

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a UserProfile when a CustomUser is first created,
    and handle updates accordingly.
    """
    if created:
        profile, created_flag = UserProfile.objects.get_or_create(user=instance)
        if created_flag:
            logger.info(f"UserProfile created for new user with ID {instance.id}")
        else:
            logger.info(f"UserProfile already existed for user with ID {instance.id}")

        event_type = 'created'
        message = f"Welcome to the platform, {instance.username}!"
    else:
        event_type = 'updated'
        message = f"Your profile has been updated."

    # Trigger a Celery task for user creation or update
    process_user_event_task.delay(instance.id, event_type)

    # Send WebSocket notification
    user_group_name = get_user_group_name(instance.id)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        user_group_name,
        {
            'type': 'user_notification',
            'message': message,
            'event': event_type,
            'user_id': str(instance.id),
            'username': instance.username,
        }
    )
    logger.info(f"Real-time WebSocket notification sent for user {event_type} with ID {instance.id}")


@receiver(soft_delete, sender=CustomUser)
def handle_soft_delete_user(sender, instance, **kwargs):
    """
    Custom signal handler to process soft deletion of CustomUser.
    """
    try:
        # Trigger Celery task to handle the user soft deletion event
        process_user_event_task.delay(instance.id, 'soft_deleted_user')

        # Send WebSocket notification for user soft deletion
        user_group_name = get_user_group_name(instance.id)  # Use utility function
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'user_notification',
                'message': "Your account has been soft-deleted.",
                'event': 'soft_deleted_user',
                'user_id': str(instance.id),
                'username': instance.username,
            }
        )
        logger.info(f"Real-time WebSocket notification sent for user soft deletion with ID {instance.id}")

    except Exception as e:
        logger.error(f"Error handling soft delete for user ID {instance.id}: {e}")


@receiver(restore, sender=CustomUser)
def handle_restore_user(sender, instance, **kwargs):
    """
    Custom signal handler to process restoration of a soft-deleted CustomUser.
    """
    try:
        # Trigger Celery task to handle the user restoration event
        process_user_event_task.delay(instance.id, 'restored_user')

        # Send WebSocket notification for user restoration
        user_group_name = get_user_group_name(instance.id)  # Use utility function
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'user_notification',
                'message': "Your account has been restored.",
                'event': 'restored_user',
                'user_id': str(instance.id),
                'username': instance.username,
            }
        )
        logger.info(f"Real-time WebSocket notification sent for user restoration with ID {instance.id}")

    except Exception as e:
        logger.error(f"Error handling restore for user ID {instance.id}: {e}")


# ===========================
# Story Signals
# ===========================

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
        send_story_shared_event_task.delay(instance.id, event_type)

    except Exception as e:
        logger.error(f"Error in story_saved signal: {e}")


@receiver(soft_delete, sender=Story)
def story_soft_deleted(sender, instance, **kwargs):
    """
    Custom signal handler to process soft deletion of Story.
    """
    try:
        # Fetching user username directly from the related User model
        user_username = instance.user.username

        # Log delete details
        logger.info(
            f"Story soft-deleted with ID: {instance.id}, User: {user_username}, "
            f"Content: {(instance.content[:30] + '...') if instance.content else 'No Content'}"
        )

        # Trigger Celery task to send story soft-deleted event to Kafka
        send_story_shared_event_task.delay(instance.id, 'soft_deleted')

    except Exception as e:
        logger.error(f"Error in story_soft_deleted signal: {e}")


@receiver(restore, sender=Story)
def story_restored(sender, instance, **kwargs):
    """
    Custom signal handler to process restoration of a soft-deleted Story.
    """
    try:
        # Fetching user username directly from the related User model
        user_username = instance.user.username

        # Log restore details
        logger.info(
            f"Story restored with ID: {instance.id}, User: {user_username}, "
            f"Content: {(instance.content[:30] + '...') if instance.content else 'No Content'}"
        )

        # Trigger Celery task to send story restored event to Kafka
        send_story_shared_event_task.delay(instance.id, 'restored')

    except Exception as e:
        logger.error(f"Error in story_restored signal: {e}")
