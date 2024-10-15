import json
import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from messenger.consumers import ChatConsumer
from config.asgi import application

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_chat_consumer():
    user = await database_sync_to_async(User.objects.create_user)(
        username='testuser', email='user@example.com', password='testpassword'
    )

    # Create a WebSocket communicator
    communicator = WebsocketCommunicator(application, f"/ws/messenger/room_name/")
    connected, subprotocol = await communicator.connect()
    assert connected

    # Test receiving a message over the WebSocket
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "chat_room_name",
        {
            "type": "chat_message",
            "message": {"text": "This is a test message"}
        }
    )
    response = await communicator.receive_from()
    assert json.loads(response) == {
        "message": {"text": "This is a test message"}
    }

    # Close the WebSocket connection
    await communicator.disconnect()
