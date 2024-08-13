# backend/albums/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Album


@receiver(post_save, sender=Album)
def album_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    event_type = 'created' if created else 'updated'
    async_to_sync(channel_layer.group_send)(
        'albums',  # Group name to send the message to
        {
            'type': 'album_message',
            'event': event_type,
            'album': instance.id,
            'title': instance.title,
            'description': instance.description,
        }
    )


@receiver(post_delete, sender=Album)
def album_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'albums',
        {
            'type': 'album_message',
            'event': 'deleted',
            'album': instance.id,
            'title': instance.title,
            'description': instance.description,
        }
    )
