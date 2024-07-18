# notifications/utils.py
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model

User = get_user_model()


def create_notification(recipient, actor, verb, target=None):
    notification = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        target=target,
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{recipient.id}',
        {
            'type': 'notify',
            'content': {
                'recipient': recipient.id,
                'actor': actor.username,
                'verb': verb,
                'target': target,
            }
        }
    )
