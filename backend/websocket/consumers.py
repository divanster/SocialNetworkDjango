import json
import logging
import jwt
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from users.models import CustomUser  # Ensure you use your custom user model
from django.conf import settings
from rest_framework_simplejwt.exceptions import \
    TokenError  # Import TokenError from simplejwt
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
            await self.close(
                code=4001)  # Close with 4001 error code (group name missing)
            return

        # Extract JWT token from query parameters
        query_string = self.scope[
            'query_string'].decode()  # Get query string from the URL
        token_param = next(
            (param for param in query_string.split("&") if param.startswith("token=")),
            None)
        token = token_param.split("=")[1] if token_param else None

        if not token:
            logger.warning("Connection attempt without token")
            await self.close(code=4001)  # Close with 4001 error code (token not found)
            return

        logger.info(f"Received token: {token}")

        try:
            # Validate JWT Token (ensure we are verifying expiration)
            decoded_token = jwt.decode(
                token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=['HS256'],
                options={'verify_exp': True}  # Ensuring expiration is checked
            )
            user_id = decoded_token.get('user_id')
            logger.info(f"Decoded token, user ID: {user_id}")

            # Get the user from the token (use CustomUser instead of User)
            user = await sync_to_async(CustomUser.objects.get)(
                id=user_id)  # Fetch the CustomUser from DB
            if user.is_anonymous:
                raise TokenError("Invalid user from token.")
            self.scope['user'] = user  # Set user in scope
            logger.info(f"User {user.username} successfully authenticated")

        except jwt.ExpiredSignatureError:
            # Handling expired signature error explicitly
            logger.warning("Connection attempt with expired token")
            await self.close(code=4002)  # Close with 4002 error code (token expired)
            return

        except (jwt.DecodeError, TokenError, CustomUser.DoesNotExist) as e:
            logger.warning(f"Connection attempt with invalid JWT: {e}")
            await self.close(code=4001)  # Close with 4001 error code (invalid token)
            return

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
        # Permission logic for user-specific groups
        if group_name.startswith('albums_user_'):
            group_user_id = group_name.split('_')[-1]
            has_permission = str(user.id) == group_user_id
            logger.info(
                f"Permission check for user {user.username} to group {group_name}: {has_permission}")
            return has_permission

        # General group permission check for public albums
        if group_name == 'public_albums_group' and user.is_authenticated:
            return True

        # Deny access by default if no condition matches
        return False

    @staticmethod
    def generate_group_name(user_id):
        """
        Generates a secure hash-based group name.
        """
        return hashlib.sha256(
            f"secure_prefix_{user_id}".encode()).hexdigest()  # Generate group name based on user ID
