import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import TaggedItem
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class TaggingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user = self.scope["user"]
        self.item_id = self.scope['url_route']['kwargs']['item_id']
        self.group_name = f'tagging_{self.item_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        logger.info(
            f'User {self.user.id} connected to tagging for item {self.item_id}.')
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(
            f'User {self.user.id} disconnected from tagging for item {self.item_id}.')

    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'tag_created',
                'tag': data['tag']
            }
        )

    async def tag_created(self, event):
        await self.send(text_data=json.dumps({
            'tag': event['tag']
        }))
