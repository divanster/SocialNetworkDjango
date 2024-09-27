# backend/users/tests/test_consumers.py

import json
from django.test import TransactionTestCase
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.urls import re_path
from users.consumers import UserConsumer
from django.conf import settings
from unittest.mock import patch
import logging

# Configure logging for the test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define application for testing
from channels.routing import ProtocolTypeRouter, URLRouter

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        re_path(r'^ws/users/$', UserConsumer.as_asgi()),
    ]),
})

class UserConsumerTests(TransactionTestCase):
    async def test_connect_and_disconnect(self):
        communicator = WebsocketCommunicator(application, "/ws/users/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_receive_new_user_event(self):
        communicator = WebsocketCommunicator(application, "/ws/users/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send a 'new_user' event
        event_data = {
            'event_type': 'new_user',
            'user': {
                'username': 'testuser',
                'email': 'testuser@example.com',
            }
        }
        await communicator.send_json_to(event_data)

        # Receive the echoed 'new_user' event
        response = await communicator.receive_json_from()
        self.assertEqual(response['event'], 'new_user')
        self.assertEqual(response['user']['username'], 'testuser')

        await communicator.disconnect()

    async def test_receive_update_user_event(self):
        communicator = WebsocketCommunicator(application, "/ws/users/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send an 'update_user' event
        event_data = {
            'event_type': 'update_user',
            'user': {
                'username': 'updateduser',
                'email': 'updateduser@example.com',
            }
        }
        await communicator.send_json_to(event_data)

        # Receive the echoed 'update_user' event
        response = await communicator.receive_json_from()
        self.assertEqual(response['event'], 'update_user')
        self.assertEqual(response['user']['username'], 'updateduser')

        await communicator.disconnect()

    async def test_receive_invalid_json(self):
        communicator = WebsocketCommunicator(application, "/ws/users/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send invalid JSON data
        await communicator.send_to(b'Invalid JSON')

        # Receive the error message
        response = await communicator.receive_json_from()
        self.assertEqual(response['error'], 'Invalid JSON format')

        await communicator.send_to('Invalid JSON')

    async def test_handle_unknown_event(self):
        communicator = WebsocketCommunicator(application, "/ws/users/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send an event with an unknown event_type
        event_data = {
            'event_type': 'unknown_event',
            'user': {
                'username': 'unknownuser',
                'email': 'unknownuser@example.com',
            }
        }
        await communicator.send_json_to(event_data)

        # Receive the unknown event response
        response = await communicator.receive_json_from()
        self.assertEqual(response['event'], 'unknown_event')
        self.assertEqual(response['error'], 'Unknown event type')

        await communicator.disconnect()
