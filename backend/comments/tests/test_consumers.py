# backend/comments/tests/test_consumers.py
import json
import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from comments.consumers import CommentConsumer
from config.asgi import application

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_comment_consumer():
    user = await database_sync_to_async(User.objects.create_user)(
        username='testuser', email='user@example.com', password='testpassword'
    )

    communicator = WebsocketCommunicator(application, "/ws/comments/")
    connected, subprotocol = await communicator.connect()
    assert connected

    # Test receiving a message over the WebSocket
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "comments",
        {
            "type": "comment_message",
            "message": {"comment": "This is a test comment"}
        }
    )
    response = await communicator.receive_from()
    assert json.loads(response) == {
        "message": {"comment": "This is a test comment"}
    }

    # Close the WebSocket connection
    await communicator.disconnect()
