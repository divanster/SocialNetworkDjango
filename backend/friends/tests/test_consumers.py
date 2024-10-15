import json
import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from friends.consumers import FriendRequestConsumer
from config.asgi import application

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_friend_request_consumer():
    user = await database_sync_to_async(User.objects.create_user)(
        username='testuser', email='user@example.com', password='testpassword'
    )

    communicator = WebsocketCommunicator(application, f"/ws/friends/{user.id}/")
    connected, subprotocol = await communicator.connect()
    assert connected

    # Test receiving a friend request created message over the WebSocket
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"friend_requests_{user.id}",
        {
            "type": "friend_request_message",
            "message": {"friend_request": "This is a test friend request",
                        "event": "created"}
        }
    )
    response = await communicator.receive_from()
    assert json.loads(response) == {
        "message": {"friend_request": "This is a test friend request",
                    "event": "created"}
    }

    # Test receiving a friend request updated message over the WebSocket
    await channel_layer.group_send(
        f"friend_requests_{user.id}",
        {
            "type": "friend_request_message",
            "message": {"friend_request": "This is an updated friend request",
                        "event": "updated"}
        }
    )
    response = await communicator.receive_from()
    assert json.loads(response) == {
        "message": {"friend_request": "This is an updated friend request",
                    "event": "updated"}
    }

    # Close the WebSocket connection
    await communicator.disconnect()
    assert communicator.is_closed()
