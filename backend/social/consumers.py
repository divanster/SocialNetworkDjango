# albums/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json


class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs'].get('post_id')
        self.group_name = f'post_{self.post_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle message for specific post
        await self.send(text_data=json.dumps({
            'message': data.get('message')
        }))


class AllPostsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'posts_all'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle general posts message
        await self.send(text_data=json.dumps({
            'message': data.get('message')
        }))
