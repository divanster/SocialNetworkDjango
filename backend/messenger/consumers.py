import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

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
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', None)
        message_id = text_data_json.get('message_id', None)
        typing = text_data_json.get('typing', None)

        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )
        elif message_id:
            await self.mark_message_as_read(message_id)
        elif typing is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'user': self.scope['user'].username,
                    'typing': typing
                }
            )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def mark_message_as_read(self, message_id):
        """Mark a message as read and notify the group."""
        message = await database_sync_to_async(Message.objects.get)(id=message_id)
        message.read_at = timezone.now()
        await database_sync_to_async(message.save)()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt',
                'message_id': message_id,
                'read_at': message.read_at.isoformat()
            }
        )

    async def read_receipt(self, event):
        """Send read receipt to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'read_at': event['read_at']
        }))

    async def typing_status(self, event):
        """Send typing status to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'user': event['user'],
            'typing': event['typing']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f'user_notifications_{self.user.id}'

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
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_notification',
                'message': data['message']
            }
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'comments'

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
                'type': 'new_comment',
                'comment': data['comment']
            }
        )

    async def new_comment(self, event):
        await self.send(text_data=json.dumps({
            'comment': event['comment']
        }))


class ActivityStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f'user_activity_{self.user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'user_status',
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'user_status',
                'status': 'offline'
            }
        )

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def user_status(self, event):
        status = event['status']

        await self.send(text_data=json.dumps({
            'status': status
        }))
