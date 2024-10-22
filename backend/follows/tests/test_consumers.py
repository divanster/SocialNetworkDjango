import json
import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from follows.consumers import FollowConsumer
from config.asgi import application

# Retrieve the custom User model
User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_follow_consumer():
    """
    Test case for FollowConsumer WebSocket.
    This test:
    - Connects a WebSocket client to the FollowConsumer.
    - Sends a follow event to the consumer's group.
    - Validates that the event is correctly received over the WebSocket.
    """

    # Step 1: Set up a user for the WebSocket communication
    user = await database_sync_to_async(User.objects.create_user)(
        username='testuser', email='user@example.com', password='testpassword'
    )

    # Step 2: Create a WebSocket communicator for the FollowConsumer
    communicator = WebsocketCommunicator(application, "/ws/follows/")

    # Step 3: Attempt to connect the WebSocket client
    connected, subprotocol = await communicator.connect()

    # Assert that the connection was successful
    assert connected, "WebSocket connection could not be established."

    # Step 4: Set up the channel layer to simulate sending a message to the group
    channel_layer = get_channel_layer()
    await channel_layer.group_add("follows", communicator.channel_name)

    # Step 5: Send a follow message to the channel layer group 'follows'
    follow_event = {
        "type": "follow_message",
        "message": {"follow": "Test follow event"}
    }
    await channel_layer.group_send("follows", follow_event)

    # Step 6: Receive a message from the WebSocket client and verify its content
    response = await communicator.receive_from()
    assert json.loads(response) == {
        "message": {"follow": "Test follow event"}
    }, "The received WebSocket message did not match the expected output."

    # Step 7: Clean up - Close the WebSocket connection
    await communicator.disconnect()
