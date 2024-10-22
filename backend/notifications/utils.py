from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

def create_notification(recipient, actor, verb, target=None):
    try:
        notification = Notification.objects.create(
            receiver_id=recipient.id,
            sender_id=actor.id,
            sender_username=actor.username,
            receiver_username=recipient.username,
            notification_type=verb,
            text=f"{actor.username} {verb}"
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{recipient.id}',
            {
                'type': 'notification_message',
                'message': {
                    'recipient': recipient.id,
                    'sender': actor.username,
                    'verb': verb,
                    'target': target,
                }
            }
        )
        logger.info(f"Notification created for user {recipient.username}")
    except ObjectDoesNotExist as e:
        logger.error(f"Error creating notification: {e}")
    except Exception as e:
        logger.error(f"Unexpected error creating notification: {e}")
