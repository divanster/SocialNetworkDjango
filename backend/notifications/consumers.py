import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            if not self.scope["user"].is_authenticated:
                await self.close()
                return

            self.user = self.scope["user"]
            self.room_group_name = f'notifications_{self.user.id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            logger.info(f'User {self.user.id} connected to notifications.')
            await self.accept()
        except Exception as e:
            logger.error(f"Error during WebSocket connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f'User {self.user.id} disconnected from notifications.')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'notification_message',
                    'message': data['message']
                }
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse WebSocket message: {e}")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def notification_message(self, event):
        try:
            message = event['message']
            await self.send(text_data=json.dumps({
                'message': message
            }))
            logger.info(f'Sent message to user {self.user.id}: {message}')
        except Exception as e:
            logger.error(f"Error sending notification message to user {self.user.id}: {e}")
