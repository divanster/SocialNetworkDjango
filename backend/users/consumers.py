import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from users.serializers import CustomUserSerializer

logger = logging.getLogger(__name__)

User = get_user_model()

class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'users'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connection accepted for {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket connection closed for {self.channel_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event_type = data.get('event_type', 'new_user')
            user_data = data.get('user', {})

            # Optionally process user_data here using serializers if needed
            # serializer = CustomUserSerializer(data=user_data)
            # if serializer.is_valid():
            #     user = serializer.save()
            # else:
            #     logger.error(f"Invalid user data: {serializer.errors}")
            #     await self.send(text_data=json.dumps({'error': 'Invalid user data'}))
            #     return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': event_type,
                    'user': user_data
                }
            )
            logger.info(f"Received and forwarded event '{event_type}' for user {user_data.get('username', 'Unknown')}")
        except json.JSONDecodeError:
            logger.error("Received invalid JSON")
            await self.send(text_data=json.dumps({'error': 'Invalid JSON format'}))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({'error': 'An error occurred'}))

    async def new_user(self, event):
        await self.send(text_data=json.dumps({
            'event': 'new_user',
            'user': event['user']
        }))
        logger.info(f"Sent 'new_user' event to WebSocket for user {event['user'].get('username', 'Unknown')}")

    async def update_user(self, event):
        await self.send(text_data=json.dumps({
            'event': 'update_user',
            'user': event['user']
        }))
        logger.info(f"Sent 'update_user' event to WebSocket for user {event['user'].get('username', 'Unknown')}")

    async def unknown_event(self, event):
        await self.send(text_data=json.dumps({
            'event': 'unknown_event',
            'error': 'Unknown event type'
        }))
        logger.warning("Received unknown event type")
