import pytest
import json
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from config.asgi import application
from unittest.mock import patch

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_notification_consumer_connect():
    user = await User.objects.acreate(username='testuser', email='user@example.com', password='password123')
    communicator = WebsocketCommunicator(application, f"/ws/notifications/")
    connected, _ = await communicator.connect()
    assert connected

    # Test connecting as unauthenticated user
    communicator.scope["user"] = None
    await communicator.connect()
    assert not connected

    # Disconnect the WebSocket
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_notification_consumer_receive():
    user = await User.objects.acreate(username='testuser', email='user@example.com', password='password123')
    communicator = WebsocketCommunicator(application, f"/ws/notifications/")
    communicator.scope["user"] = user
    connected, _ = await communicator.connect()
    assert connected

    # Send a message to the WebSocket
    message = {"message": "This is a test notification"}
    await communicator.send_json_to(message)
    response = await communicator.receive_json_from()

    assert response['message'] == message['message']

    # Disconnect the WebSocket
    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_notification_consumer_group_send():
    user = await User.objects.acreate(username='testuser', email='user@example.com', password='password123')
    communicator = WebsocketCommunicator(application, f"/ws/notifications/")
    communicator.scope["user"] = user
    connected, _ = await communicator.connect()
    assert connected

    # Send a message via channel layer
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"notifications_{user.id}",
        {
            "type": "notification_message",
            "message": "Group message test"
        }
    )
    response = await communicator.receive_json_from()

    assert response['message'] == "Group message test"

    # Disconnect the WebSocket
    await communicator.disconnect()
