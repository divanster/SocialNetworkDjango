# backend/newsfeed/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NewsfeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'newsfeed'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info('WebSocket connected')

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info('WebSocket disconnected')

    async def receive(self, text_data):
        data = json.loads(text_data)
        logger.info(f'Received message: {data}')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'feed_message',
                'message': data['message']
            }
        )

    async def feed_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
        logger.info(f'Sent message: {message}')
