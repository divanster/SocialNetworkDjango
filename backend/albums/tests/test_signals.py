from django.test import TestCase
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from django.urls import path
from albums.consumers import AlbumConsumer
import json
from django.contrib.auth import get_user_model

User = get_user_model()


class AlbumConsumerTest(TestCase):

    @database_sync_to_async
    async def asyncSetUp(self):
        self.application = URLRouter([
            path('ws/albums/', AlbumConsumer.as_asgi()),
        ])

    @database_sync_to_async
    async def test_album_consumer_receives_message(self):
        communicator = WebsocketCommunicator(self.application, 'ws/albums/')
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

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

        response = await communicator.receive_from()
        response_data = json.loads(response)
        self.assertEqual(response_data['event'], 'created')
        self.assertEqual(response_data['album'], 'album-id')
        self.assertEqual(response_data['title'], 'New Album')
        self.assertEqual(response_data['description'], 'Album description')
        self.assertEqual(response_data['tagged_users'], [])

        await communicator.disconnect()

    @database_sync_to_async
    async def test_album_consumer_receives_message_with_tagged_users(self):
        user1 = await self.create_user('user1@example.com', 'user1')
        user2 = await self.create_user('user2@example.com', 'user2')

        communicator = WebsocketCommunicator(self.application, 'ws/albums/')
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

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

        response = await communicator.receive_from()
        response_data = json.loads(response)
        self.assertEqual(len(response_data['tagged_users']), 2)
        tagged_usernames = [user['username'] for user in response_data['tagged_users']]
        self.assertIn('user1', tagged_usernames)
        self.assertIn('user2', tagged_usernames)

        await communicator.disconnect()

    @database_sync_to_async
    async def create_user(self, email, username):
        user = await database_sync_to_async(User.objects.create_user)(
            email=email, username=username, password='password123'
        )
        return user
