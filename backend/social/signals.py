import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Post
from tagging.models import TaggedItem
from .tasks import send_post_event_to_kafka
from core.utils import get_friends  # Utility function for getting friends
from websocket.consumers import GeneralKafkaConsumer  # Import for generating group names

logger = logging.getLogger(__name__)

def send_real_time_update(group_name, event_type, post):
    """
    Helper function to send real-time updates via Django Channels.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'post_message',
            'event': event_type,
            'post': str(post.id),
            'title': post.title,
            'content': post.content,
        }
    )
    logger.info(f"Real-time {event_type} update sent to {group_name} for post ID {post.id}")


# Signals for the Post model
@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    try:
        # Trigger the Celery task to send the event to Kafka
        send_post_event_to_kafka.delay(instance.id, event_type)
        logger.info(f"Triggered Celery task for post {event_type} event with ID {instance.id}")

        # Real-time update based on visibility
        if instance.visibility == 'public':
            send_real_time_update('posts_updates', event_type, instance)
        elif instance.visibility == 'friends':
            friends = get_friends(instance.author)
            for friend in friends:
                user_group_name = GeneralKafkaConsumer.generate_group_name(friend.id)
                send_real_time_update(user_group_name, event_type, instance)
        elif instance.visibility == 'private':
            user_group_name = GeneralKafkaConsumer.generate_group_name(instance.author.id)
            send_real_time_update(user_group_name, event_type, instance)

    except Exception as e:
        logger.error(f"Error handling post {event_type} signal for post ID {instance.id}: {e}")


@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    try:
        # Trigger the Celery task to send the deleted event to Kafka
        send_post_event_to_kafka.delay(instance.id, 'deleted')
        logger.info(f"Triggered Celery task for deleted post event with ID {instance.id}")

        # Real-time delete notification based on visibility
        if instance.visibility == 'public':
            send_real_time_update('posts_updates', 'deleted', instance)
        elif instance.visibility == 'friends':
            friends = get_friends(instance.author)
            for friend in friends:
                user_group_name = GeneralKafkaConsumer.generate_group_name(friend.id)
                send_real_time_update(user_group_name, 'deleted', instance)
        elif instance.visibility == 'private':
            user_group_name = GeneralKafkaConsumer.generate_group_name(instance.author.id)
            send_real_time_update(user_group_name, 'deleted', instance)

    except Exception as e:
        logger.error(f"Error handling post deleted signal for post ID {instance.id}: {e}")


# Signal for TaggedItem model to send updates about tagging actions
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
                user_group_name = GeneralKafkaConsumer.generate_group_name(instance.tagged_user_id)
                async_to_sync(channel_layer.group_send)(
                    user_group_name,
                    {
                        'type': 'post_message',
                        'event': 'tagged' if created else 'untagged',
                        'post': str(post.id),
                        'title': post.title,
                        'content': post.content,
                    }
                )
                logger.info(f"Real-time tagging update sent for post ID {post.id}")
    except Exception as e:
        logger.error(f"Error handling tagged item saved signal for object ID {instance.object_id}: {e}")
