import pytest
import json
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from config.asgi import application
import asyncio

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_page_consumer_connect():
    """
    Test if the consumer successfully connects to the WebSocket and the group.
    """
    # Create a WebSocket communicator instance
    communicator = WebsocketCommunicator(application, "/ws/pages/")

    # Connect to the WebSocket
    connected, _ = await communicator.connect()
    assert connected is True

    # Verify if the group was added successfully
    channel_layer = get_channel_layer()
    group_name = 'pages'

    # Ensure that the consumer is now in the 'pages' group
    assert await channel_layer.group_has_channels(group_name,
                                                  [communicator.channel_name])

    # Close the WebSocket connection
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_page_consumer_receive():
    """
    Test the ability to send a message to the WebSocket consumer and receive it back.
    """
    # Create a WebSocket communicator instance
    communicator = WebsocketCommunicator(application, "/ws/pages/")

    # Connect to the WebSocket
    connected, _ = await communicator.connect()
    assert connected is True

    # Send a message to the WebSocket
    message = {"message": "This is a test message"}
    await communicator.send_json_to(message)

    # Receive the message from the consumer
    response = await communicator.receive_json_from()
    assert response == {"message": "This is a test message"}

    # Close the WebSocket connection
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_page_consumer_group_send():
    """
    Test if the consumer can receive a message sent to its group.
    """
    # Create a WebSocket communicator instance
    communicator = WebsocketCommunicator(application, "/ws/pages/")

    # Connect to the WebSocket
    connected, _ = await communicator.connect()
    assert connected is True

    # Retrieve the channel layer and send a message to the group
    channel_layer = get_channel_layer()
    group_name = 'pages'
    test_message = {"type": "page_message", "message": "Hello from group!"}

    # Use the channel layer to send a message to the group
    await channel_layer.group_send(group_name, test_message)

    # Receive the message from the consumer
    response = await communicator.receive_json_from()
    assert response == {"message": "Hello from group!"}

    # Close the WebSocket connection
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_page_consumer_disconnect():
    """
    Test if the consumer disconnects properly.
    """
    # Create a WebSocket communicator instance
    communicator = WebsocketCommunicator(application, "/ws/pages/")

    # Connect to the WebSocket
    connected, _ = await communicator.connect()
    assert connected is True

    # Verify if the group was added successfully
    channel_layer = get_channel_layer()
    group_name = 'pages'

    # Ensure that the consumer is now in the 'pages' group
    assert await channel_layer.group_has_channels(group_name,
                                                  [communicator.channel_name])

    # Disconnect the WebSocket
    await communicator.disconnect()

    # Ensure that the consumer has been removed from the group
    assert not await channel_layer.group_has_channels(group_name,
                                                      [communicator.channel_name])
