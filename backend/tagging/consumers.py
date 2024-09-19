# backend/tagging/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import TaggedItem
from asgiref.sync import sync_to_async


class TaggingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.item_id = self.scope['url_route']['kwargs']['item_id']
        self.group_name = f'tagging_{self.item_id}'

        # Join the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Here you can implement the logic for creating a tag
        # Example of broadcasting tag creation to all connected users
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'tag_created',
                'tag': data['tag']
            }
        )

    async def tag_created(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'tag': event['tag']
        }))
