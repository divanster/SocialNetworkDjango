import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.apps import apps


class FriendRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the user from the scope (Django Channels automatically handles auth)
        self.user = self.scope['user']

        # Set group name specific to the user (for friend request notifications)
        self.room_group_name = f'friend_requests_{self.user.id}'

        # Add the user to the WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the WebSocket group when disconnecting
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Corrected receive signature to match the base class
    async def receive(self, text_data=None, bytes_data=None):
        # Receive and process the WebSocket message from the frontend
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'send_friend_request':
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')

            # Get the sender and receiver as User objects
            sender = await self.get_user(sender_id)
            receiver = await self.get_user(receiver_id)

            if sender and receiver:
                # Check if one of the users has blocked the other
                if await self.is_blocked(sender, receiver):
                    await self.send(text_data=json.dumps({
                        'error': 'Cannot send friend request. One of the users is blocked.'
                    }))
                else:
                    # Create a friend request in the database
                    await self.create_friend_request(sender, receiver)
                    # Notify the receiver of the new friend request
                    await self.notify_receiver(receiver_id, sender)

    async def notify_receiver(self, receiver_id, sender):
        # Notify the receiver via the WebSocket channel
        await self.channel_layer.group_send(
            f'friend_requests_{receiver_id}',
            {
                'type': 'friend_request_message',
                'message': f"{sender.username} has sent you a friend request.",
                'sender': sender.username
            }
        )

    async def friend_request_message(self, event):
        # Send the notification message to the receiver's WebSocket connection
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'sender': sender,
            'message': message
        }))

    @sync_to_async
    def create_friend_request(self, sender, receiver):
        # Load models dynamically
        FriendRequest = apps.get_model('friends', 'FriendRequest')
        try:
            # Create the friend request and save it to the database
            friend_request = FriendRequest.objects.create(sender=sender,
                                                          receiver=receiver)
            return friend_request
        except ValidationError as e:
            # Return None if validation fails
            return None

    @sync_to_async
    def is_blocked(self, sender, receiver):
        # Load models dynamically
        Block = apps.get_model('friends', 'Block')
        # Check if either user has blocked the other
        return Block.objects.filter(blocker=sender, blocked=receiver).exists() or \
            Block.objects.filter(blocker=receiver, blocked=sender).exists()

    @sync_to_async
    def get_user(self, user_id):
        User = self.get_user_model()
        try:
            # Fetch the user by ID
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            # Return None if the user does not exist
            return None

    def get_user_model(self):
        # Dynamically get the User model
        from django.contrib.auth import get_user_model
        return get_user_model()
