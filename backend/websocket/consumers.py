# backend/websocket/consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class GeneralKafkaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles the WebSocket connection initiation.
        """
        logger.info("Attempting to connect WebSocket...")

        # Extract group name from the URL parameter
        self.group_name = self.scope['url_route']['kwargs'].get('group_name', None)
        if not self.group_name:
            logger.warning("Connection attempt without group name")
            await self.close(
                code=4001)  # Close with 4001 error code (group name missing)
            return

        user = self.scope['user']

        if not user.is_authenticated:
            logger.warning("Connection attempt by unauthenticated user")
            await self.close(
                code=4001)  # Close with 4001 error code (authentication failed)
            return

        logger.info(f"User {user.username} is authenticated")

        # Perform permission check
        if not await self.has_permission(user, self.group_name):
            logger.warning(
                f"User {user.username} lacks permission to join group: {self.group_name}")
            await self.close(
                code=4003)  # Close with 4003 error code (permission denied)
            return

        # Join the group if permission is granted
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()  # Accept the WebSocket connection
        logger.info(f"User {user.username} connected to group: {self.group_name}")

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        """
        await self.channel_layer.group_discard(self.group_name,
                                               self.channel_name)  # Remove from group
        logger.info(f"User disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        """
        Receives Kafka messages from the Channels layer and forwards them to the WebSocket.
        """
        message = event.get('message', {})
        logger.debug(f"Received Kafka message for group {self.group_name}: {message}")

        # Send message to the WebSocket client
        try:
            await self.send(
                text_data=json.dumps({'message': message}))  # Send the message
            logger.debug(
                f"Message sent to WebSocket from group {self.group_name}: {message}")
        except Exception as e:
            logger.error(f"Error sending message to WebSocket client: {e}")

    async def has_permission(self, user, group_name):
        """
        Checks if the user has permission to join the group.
        """
        if group_name in ['posts', 'albums']:
            # Allow authenticated users to join 'posts' and 'albums' groups
            return user.is_authenticated

        # Example for user-specific group permission check
        if group_name.startswith('albums_user_'):
            group_user_id = group_name.split('_')[-1]
            return str(user.id) == group_user_id

        # Deny access by default
        return False
