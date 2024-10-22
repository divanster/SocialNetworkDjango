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
    """
    Test case for the FriendRequestConsumer WebSocket consumer.
    This test verifies that the consumer correctly connects, receives, and sends messages.
    """

    # Create a test user asynchronously to simulate WebSocket authentication
    user = await database_sync_to_async(User.objects.create_user)(
        username='testuser', email='user@example.com', password='testpassword'
    )

    # Set up WebSocket communicator with the ASGI application and target endpoint
    communicator = WebsocketCommunicator(application, f"/ws/friends/{user.id}/")
    connected, subprotocol = await communicator.connect()

    # Ensure that the WebSocket connection is successful
    assert connected

    # Test sending and receiving a "friend request created" message
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"friend_requests_{user.id}",  # Send to the user's specific group
        {
            "type": "friend_request_message",  # Event type as handled in consumer
            "message": {"friend_request": "This is a test friend request", "event": "created"}
        }
    )

    # Wait to receive message from WebSocket
    response = await communicator.receive_from()
    assert json.loads(response) == {
        "message": {"friend_request": "This is a test friend request", "event": "created"}
    }

    # Test sending and receiving an "updated friend request" message
    await channel_layer.group_send(
        f"friend_requests_{user.id}",  # Send to the same user group
        {
            "type": "friend_request_message",
            "message": {"friend_request": "This is an updated friend request", "event": "updated"}
        }
    )

    # Wait to receive the updated friend request from the WebSocket
    response = await communicator.receive_from()
    assert json.loads(response) == {
        "message": {"friend_request": "This is an updated friend request", "event": "updated"}
    }

    # Close the WebSocket connection and ensure it is properly closed
    await communicator.disconnect()
    assert communicator.is_closed()
