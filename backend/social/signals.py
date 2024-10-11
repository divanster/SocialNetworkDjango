from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Post
from tagging.models import TaggedItem
from django.contrib.contenttypes.models import ContentType
from .tasks import send_post_event_to_kafka


@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    # Send event to Kafka
    event_type = 'created' if created else 'updated'
    send_post_event_to_kafka.delay(instance.id, event_type)

    # Send real-time update
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'posts',
        {
            'type': 'post_message',
            'event': event_type,
            'post': str(instance.id),
            'title': instance.title,
            'content': instance.content,
        }
    )


@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    # Send event to Kafka
    send_post_event_to_kafka.delay(instance.id, 'deleted')

    # Send real-time delete notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'posts',
        {
            'type': 'post_message',
            'event': 'deleted',
            'post': str(instance.id),
            'title': instance.title,
            'content': instance.content,
        }
    )


@receiver(post_save, sender=TaggedItem)
def tagged_item_saved(sender, instance, created, **kwargs):
    if instance.content_type.model == 'post':
        # Real-time update for tagged users
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
