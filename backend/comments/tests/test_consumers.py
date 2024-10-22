# backend/comments/tests/test_consumers.py

import json
import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from comments.consumers import CommentConsumer
from config.asgi import application

# Get the user model from Django's auth system
User = get_user_model()


# Mark this test function as asyncio compatible
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_comment_consumer():
    """
    Integration test for the CommentConsumer.
    - Creates a user.
    - Establishes a WebSocket connection with the consumer.
    - Sends a message to the consumer's group and ensures that the message is received correctly.
    """

    # ================================
    # Step 1: Create a Test User
    # ================================
    user = await database_sync_to_async(User.objects.create_user)(
        username='testuser', email='user@example.com', password='testpassword'
    )

    # ================================
    # Step 2: Establish WebSocket Connection
    # ================================
    # Set up a WebSocket communicator to mimic the WebSocket connection to the consumer
    communicator = WebsocketCommunicator(application, "/ws/comments/")
    connected, subprotocol = await communicator.connect()
    # Assert that the WebSocket successfully connected
    assert connected, "WebSocket failed to connect"

    # ================================
    # Step 3: Send Message via Group and Verify Response
    # ================================
    # Retrieve the channel layer for sending messages to the group
    channel_layer = get_channel_layer()
    assert channel_layer is not None, "Channel layer could not be retrieved"

    # Define a test comment message to send
    test_message = {
        "comment": "This is a test comment",
        "tagged_users": []
    }

    # Send the message to the "comments" group, simulating another source sending data
    await channel_layer.group_send(
        "comments",
        {
            "type": "comment_message",
            "message": test_message
        }
    )

    # Receive the response from the WebSocket communicator
    response = await communicator.receive_from()

    # Parse the response as JSON and assert that it matches the sent message
    assert json.loads(response) == {
        "message": test_message
    }, "The response from the consumer did not match the expected message"

    # ================================
    # Step 4: Clean Up - Disconnect the WebSocket
    # ================================
    await communicator.disconnect()
