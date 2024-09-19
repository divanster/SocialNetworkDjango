# backend/albums/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async  # Correct import
from django.contrib.auth import get_user_model

User = get_user_model()


class AlbumConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'albums'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def album_message(self, event):
        # Fetch tagged users if provided
        tagged_user_ids = event.get('tagged_user_ids', [])
        tagged_users = []
        for user_id in tagged_user_ids:
            try:
                user = await self.get_user(user_id)
                tagged_users.append({'id': str(user.id), 'username': user.username})
            except User.DoesNotExist:
                continue

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'event': event['event'],
            'album': str(event['album']),
            'title': event['title'],
            'description': event['description'],
            'tagged_users': tagged_users,
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)
