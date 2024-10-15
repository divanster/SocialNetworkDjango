import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from config.asgi import application
from unittest.mock import patch
import json


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_newsfeed_consumer():
    communicator = WebsocketCommunicator(application, "/ws/newsfeed/")
    connected, subprotocol = await communicator.connect()
    assert connected

    # Simulate sending a Kafka message to the group
    channel_layer = get_channel_layer()
    event_data = {
        'type': 'feed_message',
        'message': {'content': 'Test feed content'}
    }
    await channel_layer.group_send('newsfeed', event_data)

    response = await communicator.receive_from()
    response_data = json.loads(response)
    assert response_data == {'message': {'content': 'Test feed content'}}

    await communicator.disconnect()
