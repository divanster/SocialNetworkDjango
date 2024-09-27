import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.apps import apps

logger = logging.getLogger(__name__)


class FriendRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Authentication check
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user = self.scope["user"]
        self.room_group_name = f'friend_requests_{self.user.id}'

        # Add the user to the WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        logger.info(f'User {self.user.id} connected to friend request notifications.')
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the WebSocket group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(
            f'User {self.user.id} disconnected from friend request notifications.')

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'send_friend_request':
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')

            sender = await self.get_user(sender_id)
            receiver = await self.get_user(receiver_id)

            if sender and receiver:
                if await self.is_blocked(sender, receiver):
                    await self.send(text_data=json.dumps({
                        'error': 'Cannot send friend request. One of the users is blocked.'
                    }))
                else:
                    await self.create_friend_request(sender, receiver)
                    await self.notify_receiver(receiver_id, sender)

    async def notify_receiver(self, receiver_id, sender):
        await self.channel_layer.group_send(
            f'friend_requests_{receiver_id}',
            {
                'type': 'friend_request_message',
                'message': f"{sender.username} has sent you a friend request.",
                'sender': sender.username
            }
        )

    async def friend_request_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'sender': sender,
            'message': message
        }))

    @sync_to_async
    def create_friend_request(self, sender, receiver):
        FriendRequest = apps.get_model('friends', 'FriendRequest')
        try:
            friend_request = FriendRequest.objects.create(sender=sender,
                                                          receiver=receiver)
            return friend_request
        except ValidationError:
            return None

    @sync_to_async
    def is_blocked(self, sender, receiver):
        Block = apps.get_model('friends', 'Block')
        return Block.objects.filter(blocker=sender, blocked=receiver).exists() or \
            Block.objects.filter(blocker=receiver, blocked=sender).exists()

    @sync_to_async
    def get_user(self, user_id):
        User = self.get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user_model(self):
        from django.contrib.auth import get_user_model
        return get_user_model()
