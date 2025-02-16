import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)
User = get_user_model()


class BaseConsumer(AsyncWebsocketConsumer):
    """
    Base WebSocket consumer that handles common logic for all consumers.
    """

    async def connect(self):
        """
        Adds the channel to a group and accepts the connection.
        """
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Removes the channel from the group on disconnect.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def kafka_message(self, event):
        """
        Handles messages sent to the WebSocket group from Kafka.
        """
        message = event['message']
        await self.send(text_data=json.dumps(message))


class AuthenticatedWebsocketConsumer(BaseConsumer):
    """
    A WebSocket consumer that handles authentication using JWT tokens.
    """

    async def connect(self):
        """
        Handles the WebSocket connection after validating the JWT token.
        """
        user = await self.authenticate_user()
        if user:
            self.scope['user'] = user
            await super().connect()
            logger.info(f"WebSocket connected for user: {user.username}")
        else:
            logger.warning("Authentication failed, rejecting connection.")
            await self.close()

    async def authenticate_user(self):
        """
        Validates the JWT token passed in the WebSocket query string.
        """
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        token = params.get('token')

        if token:
            token = token[0]
            logger.info(f"Received token: {token[:10]}...")  # Log the token (partial for security)

            try:
                UntypedToken(token)  # Validate the token format
                decoded = TokenBackend(algorithm=settings.SIMPLE_JWT['ALGORITHM']).decode(token, verify=True)
                logger.info(f"Decoded JWT Token: {decoded}")
                user = await self.get_user(decoded['user_id'])
                if user:
                    return user
                else:
                    logger.warning(f"User with ID {decoded['user_id']} not found.")
            except (InvalidToken, TokenError) as e:
                logger.warning(f"Invalid token error: {e}")
                await self.close()  # Close the connection if token is invalid
        else:
            logger.warning("Token not provided.")
        return None



# Example of other consumers inheriting from BaseConsumer
class PostConsumer(BaseConsumer):
    group_name = 'posts'


class AlbumConsumer(BaseConsumer):
    group_name = 'albums'


class CommentConsumer(BaseConsumer):
    group_name = 'comments'


class FollowConsumer(BaseConsumer):
    group_name = 'follows'


class FriendConsumer(BaseConsumer):
    group_name = 'friends'


class MessengerConsumer(BaseConsumer):
    group_name = 'messenger'


class NewsfeedConsumer(BaseConsumer):
    group_name = 'newsfeed'


class ReactionConsumer(BaseConsumer):
    group_name = 'reactions'


class SocialConsumer(BaseConsumer):
    group_name = 'social'


class StoryConsumer(BaseConsumer):
    group_name = 'stories'


class TaggingConsumer(BaseConsumer):
    group_name = 'tagging'


class UserConsumer(BaseConsumer):
    group_name = 'users'

    async def connect(self):
        """
        Add user to group and notify others when they are online.
        """
        self.user_id = self.scope["user"].id
        await super().connect()

        await self.channel_layer.group_send(self.group_name, {
            'type': 'user_online',
            'user_id': self.user_id,
        })

    async def disconnect(self, close_code):
        """
        Notify others when the user goes offline.
        """
        await self.channel_layer.group_send(self.group_name, {
            'type': 'user_offline',
            'user_id': self.user_id,
        })
        await super().disconnect(close_code)

    async def user_online(self, event):
        """
        Handle when a user comes online.
        """
        user_id = event['user_id']
        await self.send(
            text_data=json.dumps({'type': 'user_online', 'user_id': user_id}))

    async def user_offline(self, event):
        """
        Handle when a user goes offline.
        """
        user_id = event['user_id']
        await self.send(
            text_data=json.dumps({'type': 'user_offline', 'user_id': user_id}))


class NotificationConsumer(BaseConsumer):
    group_name = 'notifications'


# PresenceConsumer added
class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'presence'
        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle the message received
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
