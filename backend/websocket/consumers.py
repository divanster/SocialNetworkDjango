import json
import logging
import jwt
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser, User
from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError
from cryptography.fernet import Fernet
import hashlib

logger = logging.getLogger(__name__)


class GeneralKafkaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles the WebSocket connection initiation.
        """
        # Extract group name from the URL parameter
        self.group_name = self.scope['url_route']['kwargs'].get('group_name', None)
        if not self.group_name:
            logger.warning("Connection attempt without group name")
            await self.close(code=4001)
            return

        # Extract JWT token from query params
        query_string = self.scope['query_string'].decode()
        token_param = next(
            (param for param in query_string.split("&") if param.startswith("token=")),
            None)
        token = token_param.split("=")[1] if token_param else None

        if not token:
            logger.warning("Connection attempt without token")
            await self.close(code=4001)
            return

        try:
            # Validate JWT Token
            decoded_token = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'],
                                       algorithms=['HS256'])
            user_id = decoded_token.get('user_id')

            # Get the user from the token
            user = await sync_to_async(User.objects.get)(id=user_id)
            if user.is_anonymous:
                raise TokenError("Invalid user from token.")
            self.scope['user'] = user

        except (
        jwt.DecodeError, jwt.ExpiredSignatureError, TokenError, User.DoesNotExist) as e:
            logger.warning(f"Connection attempt with invalid JWT: {e}")
            await self.close(code=4001)
            return

        # Perform permission check using a custom method
        if not await self.has_permission(user, self.group_name):
            logger.warning(
                f"User {user.username} lacks permission to join group: {self.group_name}")
            await self.close(code=4003)
            return

        # Join the group if permission is granted
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()
        logger.info(f"User {user.username} connected to group: {self.group_name}")

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"User disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        """
        Receives Kafka messages from the Channels layer and forwards them to the WebSocket.
        """
        message = event.get('message', {})

        # Send message to the WebSocket client
        try:
            await self.send(text_data=json.dumps({'message': message}))
            logger.debug(
                f"Message sent to WebSocket from group {self.group_name}: {message}")
        except Exception as e:
            logger.error(f"Error sending message to WebSocket client: {e}")

    async def has_permission(self, user, group_name):
        """
        Checks if the user has permission to join the group.
        """
        # Example: Permission for user-specific groups
        if group_name.startswith('albums_user_'):
            group_user_id = group_name.split('_')[-1]
            has_permission = str(user.id) == group_user_id
            logger.info(
                f"Permission check for user {user.username} to group {group_name}: {has_permission}")
            return has_permission

        # General group permission check
        if group_name == 'public_albums_group' and user.is_authenticated:
            return True

        # Deny access by default
        return False

    @staticmethod
    def generate_group_name(user_id):
        """
        Generates a secure hash-based group name.
        """
        return hashlib.sha256(f"secure_prefix_{user_id}".encode()).hexdigest()
