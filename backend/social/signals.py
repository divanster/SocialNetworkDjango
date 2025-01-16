# backend/social/signals.py

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Post
from tagging.models import TaggedItem
from kafka_app.tasks.newsfeed_tasks import send_newsfeed_event_task
from kafka_app.tasks.social_tasks import process_post_event_task  # Updated import
from core.utils import get_friends  # Import the utility function for getting friends
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from kafka_app.constants import (
    TAGGING_CREATED,
    TAGGING_DELETED,
    SOCIAL_EVENTS
)

logger = logging.getLogger(__name__)


# Signals for the Post model
@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    try:
        # Define specific event types
        event_type = 'created' if created else 'updated'  # Consider defining SOCIAL_EVENTS constants

        # Trigger the Celery task to send the event to Kafka
        process_post_event_task.delay(str(instance.id), event_type)
        logger.info(
            f"Triggered Celery task for post {event_type} event with ID {instance.id}"
        )

        # Send real-time update via Django Channels respecting post visibility
        channel_layer = get_channel_layer()

        if instance.visibility == 'public':
            # Public posts are broadcast to everyone
            async_to_sync(channel_layer.group_send)(
                'posts_updates',  # Group name for posts updates
                {
                    'type': 'post_message',
                    'event': event_type,
                    'post': str(instance.id),
                    'title': instance.title,
                    'content': instance.content,
                }
            )
            logger.info(
                f"Real-time update sent via Django Channels for public post {event_type} event with ID {instance.id}"
            )

        elif instance.visibility == 'friends':
            # Notify friends of the author using utility function
            friends = get_friends(instance.author)
            for friend in friends:
                async_to_sync(channel_layer.group_send)(
                    f'user_{friend.id}_updates',  # Group per friend's updates
                    {
                        'type': 'post_message',
                        'event': event_type,
                        'post': str(instance.id),
                        'title': instance.title,
                        'content': instance.content,
                    }
                )
            logger.info(
                f"Real-time update sent to friends for post {event_type} event with ID {instance.id}"
            )

        elif instance.visibility == 'private':
            # Only notify the author for their own private posts
            async_to_sync(channel_layer.group_send)(
                f'user_{instance.author.id}_updates',  # Author's updates group
                {
                    'type': 'post_message',
                    'event': event_type,
                    'post': str(instance.id),
                    'title': instance.title,
                    'content': instance.content,
                }
            )
            logger.info(
                f"Real-time update sent to the author for private post {event_type} event with ID {instance.id}"
            )

    except Exception as e:
        logger.error(
            f"Error handling post {event_type} signal for post ID {instance.id}: {e}"
        )


@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    try:
        # Define specific event type
        event_type = 'deleted'  # Consider defining SOCIAL_EVENTS_DELETED

        # Trigger the Celery task to send the deleted event to Kafka
        process_post_event_task.delay(str(instance.id), event_type)
        logger.info(
            f"Triggered Celery task for post deleted event with ID {instance.id}"
        )

        # Send real-time delete notification via Django Channels
        channel_layer = get_channel_layer()

        if instance.visibility == 'public':
            # Public posts are broadcast to everyone
            async_to_sync(channel_layer.group_send)(
                'posts_updates',
                {
                    'type': 'post_message',
                    'event': event_type,
                    'post': str(instance.id),
                    'title': instance.title,
                    'content': instance.content,
                }
            )
            logger.info(
                f"Real-time delete notification sent via Django Channels for post ID {instance.id}"
            )

        elif instance.visibility == 'friends':
            # Notify friends of the author using utility function
            friends = get_friends(instance.author)
            for friend in friends:
                async_to_sync(channel_layer.group_send)(
                    f'user_{friend.id}_updates',
                    {
                        'type': 'post_message',
                        'event': event_type,
                        'post': str(instance.id),
                        'title': instance.title,
                        'content': instance.content,
                    }
                )
            logger.info(
                f"Real-time delete notification sent to friends for post ID {instance.id}"
            )

        elif instance.visibility == 'private':
            # Only notify the author for their own private posts
            async_to_sync(channel_layer.group_send)(
                f'user_{instance.author.id}_updates',
                {
                    'type': 'post_message',
                    'event': event_type,
                    'post': str(instance.id),
                    'title': instance.title,
                    'content': instance.content,
                }
            )
            logger.info(
                f"Real-time delete notification sent to the author for private post {event_type} event with ID {instance.id}"
            )

    except Exception as e:
        logger.error(
            f"Error handling post deleted signal for post ID {instance.id}: {e}"
        )


# Signals for the TaggedItem model
@receiver(post_save, sender=TaggedItem)
def tagged_item_saved(sender, instance, created, **kwargs):
    try:
        # Check if the content type is for Post model
        if instance.content_type.model == 'post':
            # Fetching the associated post object to ensure the attributes exist
            post = instance.content_object
            if post:
                # Real-time update for tagged users
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'posts_updates',
                    {
                        'type': 'post_message',
                        'event': TAGGING_CREATED if created else 'untagged',
                        'post': str(post.id),
                        'title': post.title,
                        'content': post.content,
                        'tagged_user_ids': [str(instance.tagged_user_id)],
                    }
                )
                logger.info(f"Real-time tagging update sent for post ID {post.id}")

                # Trigger the Celery task to send the tagging event to Kafka
                send_newsfeed_event_task.delay(
                    str(post.id),
                    TAGGING_CREATED if created else TAGGING_DELETED,
                    'TaggedItem'
                )
                logger.info(
                    f"Triggered Celery task for tagging event '{TAGGING_CREATED if created else TAGGING_DELETED}' on post ID {post.id}"
                )

    except Exception as e:
        logger.error(
            f"Error handling tagged item saved signal for object ID {instance.object_id}: {e}"
        )
