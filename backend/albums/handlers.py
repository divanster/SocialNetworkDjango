import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def handle_album_events(message):
    event_type = message.get('event')
    album_id = message.get('album_id')
    title = message.get('title')
    description = message.get('description')
    user_id = message.get('user_id')
    created_at = message.get('created_at')
    updated_at = message.get('updated_at')
    deleted_at = message.get('deleted_at')

    channel_layer = get_channel_layer()
    group_name = 'albums'

    if event_type == 'created':
        payload = {
            'event': 'album_created',
            'album_id': album_id,
            'title': title,
            'description': description,
            'user_id': user_id,
            'created_at': created_at,
        }
    elif event_type == 'updated':
        payload = {
            'event': 'album_updated',
            'album_id': album_id,
            'title': title,
            'description': description,
            'user_id': user_id,
            'updated_at': updated_at,
        }
    elif event_type == 'deleted':
        payload = {
            'event': 'album_deleted',
            'album_id': album_id,
            'title': title,
            'description': description,
            'user_id': user_id,
            'deleted_at': deleted_at,
        }
    else:
        logger.warning(f"Unhandled event type: {event_type}")
        return

    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'album_message',
                'message': payload
            }
        )
        logger.info(f"Relayed album event to Channels group '{group_name}': {payload}")
    except Exception as e:
        logger.error(f"Error relaying message to Channels: {e}")
