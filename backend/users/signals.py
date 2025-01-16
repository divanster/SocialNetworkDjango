# backend/users/signals.py

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser, UserProfile
from kafka_app.tasks.user_tasks import process_user_event_task  # Ensure this task exists
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from utils.group_names import get_user_group_name  # Ensure this utility exists

from core.signals import soft_delete, restore  # Ensure these custom signals exist

from kafka_app.constants import (
    USER_CREATED,
    USER_UPDATED,
    USER_SOFT_DELETED,
    USER_RESTORED
)

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
    try:
        if created:
            profile, created_flag = UserProfile.objects.get_or_create(user=instance)
            if created_flag:
                logger.info(f"UserProfile created for new user with ID {instance.id}")
            else:
                logger.info(f"UserProfile already existed for user with ID {instance.id}")

            event_type = USER_CREATED
            message = f"Welcome to the platform, {instance.username}!"
        else:
            event_type = USER_UPDATED
            message = f"Your profile has been updated."

        # Trigger a Celery task for user creation or update
        process_user_event_task.delay(str(instance.id), event_type)

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
    except Exception as e:
        logger.error(f"Error in create_or_update_user_profile signal: {e}")


@receiver(soft_delete, sender=CustomUser)
def handle_soft_delete_user(sender, instance, **kwargs):
    """
    Custom signal handler to process soft deletion of CustomUser.
    """
    try:
        # Trigger Celery task to handle the user soft deletion event
        process_user_event_task.delay(str(instance.id), USER_SOFT_DELETED)

        # Send WebSocket notification for user soft deletion
        user_group_name = get_user_group_name(instance.id)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'user_notification',
                'message': "Your account has been soft-deleted.",
                'event': USER_SOFT_DELETED,
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
        process_user_event_task.delay(str(instance.id), USER_RESTORED)

        # Send WebSocket notification for user restoration
        user_group_name = get_user_group_name(instance.id)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'user_notification',
                'message': "Your account has been restored.",
                'event': USER_RESTORED,
                'user_id': str(instance.id),
                'username': instance.username,
            }
        )
        logger.info(f"Real-time WebSocket notification sent for user restoration with ID {instance.id}")

    except Exception as e:
        logger.error(f"Error handling restore for user ID {instance.id}: {e}")
