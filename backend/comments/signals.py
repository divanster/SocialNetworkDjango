# backend/comments/signals.py

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from comments.models import Comment
from kafka_app.tasks import process_comment_event_task
from core.signals import soft_delete, restore  # Import custom signals

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from social.models import Post
from utils.group_names import get_user_group_name  # Import utility function

logger = logging.getLogger(__name__)


# ===========================
# Comment Signals
# ===========================

@receiver(post_save, sender=Comment)
def comment_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal to handle comment creation or update.
    Triggers a Celery task to process the comment event and sends WebSocket notifications.

    Args:
        sender (Model class): The model class that sent the signal.
        instance (Comment): The actual instance being saved.
        created (bool): Boolean; True if a new record was created.
    """
    event_type = 'created' if created else 'updated'

    try:
        # Fetching user username directly from the related User model
        user_username = instance.user.username

        # Log event details
        logger.info(
            f"Comment {event_type} with ID: {instance.id}, User: {user_username}, "
            f"Content: {(instance.content[:30] + '...') if instance.content else 'No Content'}, "
            f"Related Content: {instance.content_object}"
        )

        # Trigger the Celery task for processing the event asynchronously
        process_comment_event_task.delay(instance.id, event_type)
        logger.info(
            f"[SIGNAL] Triggered Celery task for comment {event_type} with ID {instance.id}"
        )

        # Send WebSocket notification (optional)
        # Assuming comments are related to generic content types and you want to notify relevant users
        # You may need to customize this based on your application's logic
        related_user = get_related_user(instance)  # Define a method to get the related user
        if related_user:
            user_group_name = get_user_group_name(related_user.id)
            channel_layer = get_channel_layer()
            message = f"Your content has a new comment by {user_username}." if created else f"A comment on your content has been updated."
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'comment_notification',
                    'message': message,
                    'event': event_type,
                    'comment_id': str(instance.id),
                    'content_id': str(instance.object_id),
                    'user_id': str(related_user.id),
                    'username': related_user.username,
                }
            )
            logger.info(f"Real-time WebSocket notification sent for comment {event_type} with ID {instance.id}")

    except Exception as e:
        logger.error(f"Error in comment_created_or_updated signal: {e}")


@receiver(soft_delete, sender=Comment)
def comment_soft_deleted(sender, instance, **kwargs):
    """
    Custom signal handler to process soft deletion of Comment.
    Triggers a Celery task and sends WebSocket notifications.

    Args:
        sender (Model class): The model class that sent the signal.
        instance (Comment): The instance being soft-deleted.
        **kwargs: Additional keyword arguments.
    """
    try:
        # Trigger the Celery task for processing the soft deletion event asynchronously
        process_comment_event_task.delay(instance.id, 'soft_deleted')
        logger.info(
            f"[SIGNAL] Triggered Celery task for comment soft deletion with ID {instance.id}"
        )

        # Send WebSocket notification (optional)
        related_user = get_related_user(instance)  # Define a method to get the related user
        if related_user:
            user_group_name = get_user_group_name(related_user.id)
            channel_layer = get_channel_layer()
            message = f"A comment on your content has been soft-deleted."
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'comment_notification',
                    'message': message,
                    'event': 'soft_deleted',
                    'comment_id': str(instance.id),
                    'content_id': str(instance.object_id),
                    'user_id': str(related_user.id),
                    'username': related_user.username,
                }
            )
            logger.info(f"Real-time WebSocket notification sent for comment soft deletion with ID {instance.id}")

    except Exception as e:
        logger.error(f"Error in comment_soft_deleted signal: {e}")


@receiver(restore, sender=Comment)
def comment_restored(sender, instance, **kwargs):
    """
    Custom signal handler to process restoration of a soft-deleted Comment.
    Triggers a Celery task and sends WebSocket notifications.

    Args:
        sender (Model class): The model class that sent the signal.
        instance (Comment): The instance being restored.
        **kwargs: Additional keyword arguments.
    """
    try:
        # Trigger the Celery task for processing the restoration event asynchronously
        process_comment_event_task.delay(instance.id, 'restored')
        logger.info(
            f"[SIGNAL] Triggered Celery task for comment restoration with ID {instance.id}"
        )

        # Send WebSocket notification (optional)
        related_user = get_related_user(instance)  # Define a method to get the related user
        if related_user:
            user_group_name = get_user_group_name(related_user.id)
            channel_layer = get_channel_layer()
            message = f"A comment on your content has been restored."
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'comment_notification',
                    'message': message,
                    'event': 'restored',
                    'comment_id': str(instance.id),
                    'content_id': str(instance.object_id),
                    'user_id': str(related_user.id),
                    'username': related_user.username,
                }
            )
            logger.info(f"Real-time WebSocket notification sent for comment restoration with ID {instance.id}")

    except Exception as e:
        logger.error(f"Error in comment_restored signal: {e}")


# ===========================
# Helper Function to Get Related User
# ===========================

def get_related_user(comment_instance):
    """
    Retrieves the user associated with the content the comment is related to.
    This function should be customized based on how content relates to users in your application.

    Args:
        comment_instance (Comment): The comment instance.

    Returns:
        User or None: The related user or None if not found.
    """
    try:
        # Example for a Post model
        if isinstance(comment_instance.content_object, Post):
            return comment_instance.content_object.user
        # Add more content types as needed
        # elif isinstance(comment_instance.content_object, AnotherModel):
        #     return comment_instance.content_object.user
        else:
            return None
    except Exception as e:
        logger.error(f"Error in get_related_user: {e}")
        return None
