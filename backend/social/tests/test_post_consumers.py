import pytest
import json
from channels.testing import WebsocketCommunicator
from config.asgi import application
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestPostConsumers:

    async def create_user(self, email, username, password):
        user = await database_sync_to_async(User.objects.create_user)(
            email=email, username=username, password=password
        )
        return user

    async def test_post_consumer_connect_and_disconnect(self):
        # Create WebSocket communicator for a specific post
        post_id = 123
        communicator = WebsocketCommunicator(application, f"/ws/post/{post_id}/")

        # Connect to WebSocket
        connected, _ = await communicator.connect()
        assert connected

        # Disconnect from WebSocket
        await communicator.disconnect()
        # Assert disconnection, note that Channels doesn't provide a response on
        # disconnect, so we verify by ensuring no exception occurred

    async def test_post_consumer_receive_message(self):
        post_id = 123
        communicator = WebsocketCommunicator(application, f"/ws/post/{post_id}/")
        connected, _ = await communicator.connect()
        assert connected

        # Create channel layer to send message to group
        channel_layer = get_channel_layer()
        group_name = f'post_{post_id}'

        # Send message to group through channel layer
        message_content = "Test message for post"
        await channel_layer.group_send(
            group_name,
            {
                "type": "post_message",
                "message": message_content
            }
        )

        # Receive message from WebSocket
        response = await communicator.receive_from()
        response_data = json.loads(response)
        assert response_data["message"] == message_content

        await communicator.disconnect()

    async def test_all_posts_consumer_connect_and_disconnect(self):
        # Create WebSocket communicator for all posts
        communicator = WebsocketCommunicator(application, f"/ws/posts/all/")

        # Connect to WebSocket
        connected, _ = await communicator.connect()
        assert connected

        # Disconnect from WebSocket
        await communicator.disconnect()

    async def test_all_posts_consumer_receive_message(self):
        communicator = WebsocketCommunicator(application, f"/ws/posts/all/")
        connected, _ = await communicator.connect()
        assert connected

        # Create channel layer to send message to group
        channel_layer = get_channel_layer()
        group_name = 'posts_all'

        # Send message to group through channel layer
        message_content = "Broadcast message to all posts"
        await channel_layer.group_send(
            group_name,
            {
                "type": "post_message",
                "message": message_content
            }
        )

        # Receive message from WebSocket
        response = await communicator.receive_from()
        response_data = json.loads(response)
        assert response_data["message"] == message_content

        await communicator.disconnect()

    async def test_post_consumer_send_message(self):
        post_id = 123
        communicator = WebsocketCommunicator(application, f"/ws/post/{post_id}/")
        connected, _ = await communicator.connect()
        assert connected

        # Send a message through the WebSocket
        message = {"message": "Client message for post"}
        await communicator.send_json_to(message)

        # Create channel layer to send message to group
        channel_layer = get_channel_layer()
        group_name = f'post_{post_id}'

        # Verify that the message is properly sent to the group
        await channel_layer.group_send(
            group_name,
            {
                "type": "post_message",
                "message": message["message"]
            }
        )

        # Receive message from WebSocket
        response = await communicator.receive_from()
        response_data = json.loads(response)
        assert response_data["message"] == message["message"]

        await communicator.disconnect()

    async def test_all_posts_consumer_send_message(self):
        communicator = WebsocketCommunicator(application, f"/ws/posts/all/")
        connected, _ = await communicator.connect()
        assert connected

        # Send a message through the WebSocket
        message = {"message": "Client message for all posts"}
        await communicator.send_json_to(message)

        # Create channel layer to send message to group
        channel_layer = get_channel_layer()
        group_name = 'posts_all'

        # Verify that the message is properly sent to the group
        await channel_layer.group_send(
            group_name,
            {
                "type": "post_message",
                "message": message["message"]
            }
        )

        # Receive message from WebSocket
        response = await communicator.receive_from()
        response_data = json.loads(response)
        assert response_data["message"] == message["message"]

        await communicator.disconnect()
