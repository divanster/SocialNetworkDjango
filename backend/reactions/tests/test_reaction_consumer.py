import pytest
import json
from channels.testing import WebsocketCommunicator
from config.asgi import application


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_reaction_consumer_connect():
    communicator = WebsocketCommunicator(application, "/ws/reactions/1/")
    connected, _ = await communicator.connect()
    assert connected

    # Send a message to the WebSocket
    message = {"message": "Reacted with 'like'"}
    await communicator.send_json_to(message)

    # Receive the echoed message back
    response = await communicator.receive_json_from()
    assert response == {"message": "Reacted with 'like'"}

    await communicator.disconnect()
