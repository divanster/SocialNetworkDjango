import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)


class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs'].get('post_id')
        self.group_name = f'post_{self.post_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Connected to WebSocket for post {self.post_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"Disconnected from WebSocket for post {self.post_id}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'post_message',
                'message': data.get('message')
            }
        )

    async def post_message(self, event):
        message = event.get('message')
        await self.send(text_data=json.dumps({
            'message': message
        }))


class AllPostsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'posts_all'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        logger.info("Connected to WebSocket for all posts")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info("Disconnected from WebSocket for all posts")

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'post_message',
                'message': data.get('message')
            }
        )

    async def post_message(self, event):
        message = event.get('message')
        await self.send(text_data=json.dumps({
            'message': message
        }))
