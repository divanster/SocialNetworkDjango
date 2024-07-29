# backend/newsfeed/signals.py
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from stories.models import Story
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

channel_layer = get_channel_layer()


@receiver(post_save, sender=Post)
@receiver(post_save, sender=Comment)
@receiver(post_save, sender=Reaction)
@receiver(post_save, sender=Album)
@receiver(post_save, sender=Story)
def update_feed(sender, instance, created, **kwargs):
    message = f'New update: {instance}'
    logger.info(message)
    async_to_sync(channel_layer.group_send)(
        'newsfeed',
        {
            'type': 'feed_message',
            'message': message
        }
    )


@receiver(post_delete, sender=Post)
@receiver(post_delete, sender=Comment)
@receiver(post_delete, sender=Reaction)
@receiver(post_delete, sender=Album)
@receiver(post_delete, sender=Story)
def remove_from_feed(sender, instance, **kwargs):
    message = f'Removed: {instance}'
    logger.info(message)
    async_to_sync(channel_layer.group_send)(
        'newsfeed',
        {
            'type': 'feed_message',
            'message': message
        }
    )
