# backend/websocket/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection

class GeneralKafkaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract group name from the URL parameter
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        user = self.scope['user']

        # Check if user is authenticated and has permission to join the group
        if not user.is_authenticated:
            await self.close(code=4001)  # Close connection if user is not authenticated
            return

        # Perform permission check using a custom method
        if not await self.has_permission(user, self.group_name):
            await self.close(code=4003)  # Close connection if user does not have permission
            return

        # If permission check passes, join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group when the WebSocket disconnects
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from the Channels layer (from KafkaConsumerApp)
    async def kafka_message(self, event):
        message = event['message']

        # Send message to the WebSocket client
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def has_permission(self, user, group_name):
        """
        Implement your logic to check if the user has permission to join the group.
        Example:
            - If the group is 'albums_user_{user_id}', ensure user_id matches the authenticated user.
            - Add other permission checks as needed.
        """
        # Example 1: Permission for user-specific groups
        if group_name.startswith('albums_user_'):
            group_user_id = group_name.split('_')[-1]
            return str(user.id) == group_user_id

        # Example 2: General group permission check (expand as needed)
        # Add any group-based or role-based permissions you require.
        if group_name == 'public_albums_group' and user.is_authenticated:
            return True

        # Deny access by default
        return False
