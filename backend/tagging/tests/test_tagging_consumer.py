# tagging/tests/test_tagging_consumer.py
import pytest
from channels.testing import WebsocketCommunicator
from tagging.consumers import TaggingConsumer
from config.asgi import application


@pytest.mark.asyncio
async def test_tagging_consumer_connect():
    communicator = WebsocketCommunicator(application, "/ws/tagging/1/")
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()


@pytest.mark.asyncio
async def test_tagging_consumer_receive():
    communicator = WebsocketCommunicator(application, "/ws/tagging/1/")
    await communicator.connect()
    message = {'tag': 'Test tag'}
    await communicator.send_json_to(message)
    response = await communicator.receive_json_from()
    assert response == {'tag': 'Test tag'}
    await communicator.disconnect()
