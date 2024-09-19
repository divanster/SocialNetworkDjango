# backend/social/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model


class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'posts'
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

    async def post_message(self, event):
        tagged_user_ids = event.get('tagged_user_ids', [])
        tagged_users = []
        for user_id in tagged_user_ids:
            try:
                user = await self.get_user(user_id)
                tagged_users.append({'id': str(user.id), 'username': user.username})
            except get_user_model().DoesNotExist:
                continue

        await self.send(text_data=json.dumps({
            'event': event['event'],
            'post': str(event['post']),
            'title': event['title'],
            'content': event['content'],
            'tagged_users': tagged_users,
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        return User.objects.get(id=user_id)
