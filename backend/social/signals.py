# backend/social/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Post
from tagging.models import TaggedItem
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    event_type = 'created' if created else 'updated'

    # Fetch tagged user IDs
    tagged_items = TaggedItem.objects.filter(
        content_type=ContentType.objects.get_for_model(Post),
        object_id=instance.id
    )
    tagged_user_ids = list(tagged_items.values_list('tagged_user_id', flat=True))

    async_to_sync(channel_layer.group_send)(
        'posts',
        {
            'type': 'post_message',
            'event': event_type,
            'post': str(instance.id),
            'title': instance.title,
            'content': instance.content,
            'tagged_user_ids': [str(user_id) for user_id in tagged_user_ids],
        }
    )


@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'posts',
        {
            'type': 'post_message',
            'event': 'deleted',
            'post': str(instance.id),
            'title': instance.title,
            'content': instance.content,
            'tagged_user_ids': [],
        }
    )


@receiver(post_save, sender=TaggedItem)
def tagged_item_saved(sender, instance, created, **kwargs):
    if instance.content_type.model == 'post':
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'posts',
            {
                'type': 'post_message',
                'event': 'tagged' if created else 'untagged',
                'post': str(instance.object_id),
                'title': instance.content_object.title,
                'content': instance.content_object.content,
                'tagged_user_ids': [str(instance.tagged_user_id)],
            }
        )
