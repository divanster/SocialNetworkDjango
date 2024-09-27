import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class ReactionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user = self.scope["user"]
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.room_group_name = f'reactions_{self.post_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        logger.info(
            f'User {self.user.id} connected to reactions for post {self.post_id}.')
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(
            f'User {self.user.id} disconnected from reactions for post {self.post_id}.')

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'reaction_message',
                'message': data['message']
            }
        )

    async def reaction_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
