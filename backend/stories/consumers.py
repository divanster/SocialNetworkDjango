# backend/stories/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class StoryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'stories'
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

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'story_message',
                'message': data['message']
            }
        )

    async def story_message(self, event):
        message = event['message']
        # Modify the message to include new fields
        await self.send(text_data=json.dumps({
            'message': message,
            'media_type': event.get('media_type'),
            'media_url': event.get('media_url'),
            'is_active': event.get('is_active')
        }))
