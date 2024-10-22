import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from config.asgi import application
from unittest.mock import patch
import json


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@patch(
    'newsfeed.consumers.KafkaConsumerClient')  # Patching KafkaConsumerClient to prevent real Kafka connection
async def test_newsfeed_consumer(mock_kafka_client):
    # Set up mock Kafka client
    mock_kafka_instance = mock_kafka_client.return_value
    mock_kafka_instance.consume_messages.return_value = []  # Return an empty list of messages for this test

    # Create a WebSocket communicator for the newsfeed consumer
    communicator = WebsocketCommunicator(application, "/ws/newsfeed/")
    connected, subprotocol = await communicator.connect()

    # Ensure the WebSocket connection is successfully established
    assert connected, "WebSocket connection could not be established."

    # Simulate sending a Kafka message to the group using the Channel Layer
    channel_layer = get_channel_layer()
    event_data = {
        'type': 'feed_message',
        'message': {'content': 'Test feed content'}
    }
    await channel_layer.group_send('newsfeed', event_data)

    # Await and verify the response from the WebSocket
    response = await communicator.receive_from()
    response_data = json.loads(response)
    assert response_data == {'message': {
        'content': 'Test feed content'}}, "The received message does not match the expected data."

    # Close the WebSocket connection
    await communicator.disconnect()

    # Ensure the communicator is properly closed
    assert communicator.is_closed(), "WebSocket connection did not close as expected."
