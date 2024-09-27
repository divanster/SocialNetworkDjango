# backend/friends/tests/test_consumers.py

import json
from django.test import TransactionTestCase
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from channels.routing import ProtocolTypeRouter, URLRouter
from django.contrib.auth import get_user_model
from django.urls import re_path
from asgiref.sync import sync_to_async
from friends.consumers import FriendRequestConsumer
from friends.models import FriendRequest, Block
import logging

# Configure logging for the test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

User = get_user_model()

# Define application for testing
application = ProtocolTypeRouter({
    'websocket': URLRouter([
        re_path(r'^ws/friend_requests/$', FriendRequestConsumer.as_asgi()),
    ]),
})


class FriendRequestConsumerTests(TransactionTestCase):
    async def asyncSetUp(self):
        self.channel_layer = get_channel_layer()
        await self.channel_layer.flush()
        # Create test users
        self.sender = await sync_to_async(User.objects.create_user)(
            email='sender@example.com',
            username='sender',
            password='password1'
        )
        self.receiver = await sync_to_async(User.objects.create_user)(
            email='receiver@example.com',
            username='receiver',
            password='password2'
        )
        # Set up communicators for sender and receiver
        self.sender_communicator = WebsocketCommunicator(
            application,
            "/ws/friend_requests/",
            headers=[
                (b'cookie', f'sessionid={self.client.session.session_key}'.encode())
            ]
        )
        # Authenticate the sender user
        self.client.force_login(self.sender)
        # Get the session ID
        session_id = self.client.session.session_key
        self.sender_communicator.scope['session'] = self.client.session
        self.sender_communicator.scope['user'] = self.sender
        self.sender_communicator.scope['cookies'] = {'sessionid': session_id}
        await self.sender_communicator.connect()

        # Repeat for receiver
        self.receiver_communicator = WebsocketCommunicator(
            application,
            "/ws/friend_requests/",
            headers=[
                (b'cookie', f'sessionid={self.client.session.session_key}'.encode())
            ]
        )
        self.client.force_login(self.receiver)
        session_id = self.client.session.session_key
        self.receiver_communicator.scope['session'] = self.client.session
        self.receiver_communicator.scope['user'] = self.receiver
        self.receiver_communicator.scope['cookies'] = {'sessionid': session_id}
        await self.receiver_communicator.connect()

    async def asyncTearDown(self):
        await self.sender_communicator.disconnect()
        await self.receiver_communicator.disconnect()

    async def test_send_friend_request(self):
        """
        Test that a friend request can be sent via WebSocket and that the receiver is notified.
        """
        # Sender sends a friend request to receiver
        send_data = {
            'action': 'send_friend_request',
            'sender_id': self.sender.id,
            'receiver_id': self.receiver.id
        }
        await self.sender_communicator.send_json_to(send_data)

        # Receiver should receive a notification
        response = await self.receiver_communicator.receive_json_from()
        self.assertEqual(response['sender'], self.sender.username)
        self.assertEqual(response['message'],
                         f"{self.sender.username} has sent you a friend request.")

        # Check that the friend request was created in the database
        friend_request_exists = await sync_to_async(FriendRequest.objects.filter(
            sender=self.sender,
            receiver=self.receiver
        ).exists)()
        self.assertTrue(friend_request_exists)

    async def test_send_friend_request_blocked(self):
        """
        Test that a friend request cannot be sent if one user has blocked the other.
        """
        # Block the sender
        await sync_to_async(Block.objects.create)(blocker=self.receiver,
                                                  blocked=self.sender)

        # Sender attempts to send a friend request to receiver
        send_data = {
            'action': 'send_friend_request',
            'sender_id': self.sender.id,
            'receiver_id': self.receiver.id
        }
        await self.sender_communicator.send_json_to(send_data)

        # Sender should receive an error message
        response = await self.sender_communicator.receive_json_from()
        self.assertIn('error', response)
        self.assertEqual(response['error'],
                         'Cannot send friend request. One of the users is blocked.')

        # Check that the friend request was not created in the database
        friend_request_exists = await sync_to_async(FriendRequest.objects.filter(
            sender=self.sender,
            receiver=self.receiver
        ).exists)()
        self.assertFalse(friend_request_exists)

    async def test_send_friend_request_invalid_user(self):
        """
        Test handling when the receiver does not exist.
        """
        # Sender attempts to send a friend request to a non-existent user
        send_data = {
            'action': 'send_friend_request',
            'sender_id': self.sender.id,
            'receiver_id': 9999  # Non-existent user ID
        }
        await self.sender_communicator.send_json_to(send_data)

        # Sender should receive an error message
        response = await self.sender_communicator.receive_json_from()
        self.assertIn('error', response)
        # You might want to adjust the consumer to handle this case if not already

    async def test_send_friend_request_invalid_action(self):
        """
        Test handling of an invalid action.
        """
        # Sender sends an invalid action
        send_data = {
            'action': 'invalid_action',
            'sender_id': self.sender.id,
            'receiver_id': self.receiver.id
        }
        await self.sender_communicator.send_json_to(send_data)

        # Depending on your consumer's implementation, handle this accordingly
        # For example, you might expect no response or an error message
        # Here, we will assume no response is sent
        with self.assertRaises(Exception):
            await self.sender_communicator.receive_json_from(timeout=1)
