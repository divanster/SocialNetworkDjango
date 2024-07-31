# backend/users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


@receiver(post_save, sender=CustomUser)
def send_user_update(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    user_data = {
        'id': instance.id,
        'username': instance.username,
        'email': instance.email,
        'first_name': instance.profile.first_name,
        'last_name': instance.profile.last_name,
        # Add more user fields as needed
    }

    event_type = 'new_user' if created else 'update_user'

    async_to_sync(channel_layer.group_send)(
        'users',
        {
            'type': event_type,
            'user': user_data
        }
    )
