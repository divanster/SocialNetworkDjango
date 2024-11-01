import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class GeneralKafkaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles the WebSocket connection initiation.
        """
        # Extract group name from the URL parameter
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        user = self.scope.get('user', AnonymousUser())

        # Check if user is authenticated and has permission to join the group
        if not user.is_authenticated:
            logger.warning(
                f"Connection attempt from unauthenticated user to group: {self.group_name}")
            await self.close(code=4001)  # Close connection if user is not authenticated
            return

        # Perform permission check using a custom method
        if not await self.has_permission(user, self.group_name):
            logger.warning(
                f"User {user.username} lacks permission to join group: {self.group_name}")
            await self.close(
                code=4003)  # Close connection if user does not have permission
            return

        # If permission check passes, join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()
        logger.info(f"User {user.username} connected to group: {self.group_name}")

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"User disconnected from group: {self.group_name}")

    # Receive message from the Channels layer (from KafkaConsumerApp)
    async def kafka_message(self, event):
        """
        Receives Kafka messages from the Channels layer and forwards them to the WebSocket.
        """
        message = event.get('message', {})

        # Send message to the WebSocket client
        await self.send(text_data=json.dumps({
            'message': message
        }))
        logger.debug(
            f"Message sent to WebSocket from group {self.group_name}: {message}")

    async def has_permission(self, user, group_name):
        """
        Checks if the user has permission to join the group.

        Example:
        - If the group is 'albums_user_{user_id}', ensure user_id matches the authenticated user.
        - Add other permission checks as needed.
        """
        # Example 1: Permission for user-specific groups
        if group_name.startswith('albums_user_'):
            group_user_id = group_name.split('_')[-1]
            has_permission = str(user.id) == group_user_id
            logger.info(
                f"Permission check for user {user.username} to group {group_name}: {has_permission}")
            return has_permission

        # Example 2: General group permission check (expand as needed)
        if group_name == 'public_albums_group' and user.is_authenticated:
            return True

        # Deny access by default
        return False
