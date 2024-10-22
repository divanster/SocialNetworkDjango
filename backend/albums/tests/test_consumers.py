# albums/tests/test_signals.py

import json
from django.test import TestCase
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from django.urls import path
from albums.consumers import AlbumConsumer
from django.contrib.auth import get_user_model
import pytest
from asgiref.testing import ApplicationCommunicator

User = get_user_model()


@pytest.mark.asyncio
class AlbumConsumerTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up any necessary test environment or state

    @pytest.mark.asyncio
    async def test_album_consumer_receives_message(self):
        """
        Test that the consumer properly receives and processes an album event message.
        """
        # Set up the application for testing
        application = URLRouter([
            path('ws/albums/', AlbumConsumer.as_asgi()),
        ])

        # Instantiate a WebsocketCommunicator
        communicator = WebsocketCommunicator(application, 'ws/albums/')
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Simulate sending a message to the group
        channel_layer = get_channel_layer()
        event = {
            'type': 'album_message',
            'event': 'created',
            'album': 'album-id',
            'title': 'New Album',
            'description': 'Album description',
            'tagged_user_ids': []
        }
        await channel_layer.group_send('albums', event)

        # Receive message from the WebSocket
        response = await communicator.receive_json_from()
        self.assertEqual(response['event'], 'created')
        self.assertEqual(response['album'], 'album-id')
        self.assertEqual(response['title'], 'New Album')
        self.assertEqual(response['description'], 'Album description')
        self.assertEqual(response['tagged_users'], [])

        # Close the WebSocket connection
        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_album_consumer_receives_message_with_tagged_users(self):
        """
        Test that the consumer properly receives and processes an album event message,
        with tagged users included.
        """
        # Create users
        user1 = await self.create_user('user1@example.com', 'user1')
        user2 = await self.create_user('user2@example.com', 'user2')

        # Set up the application
        application = URLRouter([
            path('ws/albums/', AlbumConsumer.as_asgi()),
        ])

        communicator = WebsocketCommunicator(application, 'ws/albums/')
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message to the group with tagged users
        channel_layer = get_channel_layer()
        event = {
            'type': 'album_message',
            'event': 'created',
            'album': 'album-id',
            'title': 'New Album',
            'description': 'Album description',
            'tagged_user_ids': [str(user1.id), str(user2.id)]
        }
        await channel_layer.group_send('albums', event)

        # Receive message
        response = await communicator.receive_json_from()
        self.assertEqual(len(response['tagged_users']), 2)
        tagged_usernames = [user['username'] for user in response['tagged_users']]
        self.assertIn('user1', tagged_usernames)
        self.assertIn('user2', tagged_usernames)

        await communicator.disconnect()

    @database_sync_to_async
    def create_user(self, email, username):
        """
        Helper function to create a user asynchronously.
        """
        user = User.objects.create_user(
            email=email,
            username=username,
            password='password123'
        )
        return user
