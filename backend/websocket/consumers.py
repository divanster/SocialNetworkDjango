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
from jwt import ExpiredSignatureError, DecodeError
from django.core.cache import cache

logger = logging.getLogger(__name__)
User = get_user_model()


class BaseConsumer(AsyncWebsocketConsumer):
    """
    Base WebSocket consumer that handles common logic for all consumers.
    Each subclass should set a 'group_name' at the class level.
    """

    group_name = None  # Subclasses will override

    async def connect(self):
        """
        Adds the channel to a group and accepts the connection.
        """
        # Instead of reading from self.scope['url_route']['kwargs']['group_name'],
        # we rely on the class-level group_name each subclass sets.
        if not self.group_name:
            # Fallback or default group name if none is set:
            self.group_name = "default"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Removes the channel from the group on disconnect.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def kafka_message(self, event):
        """
        Handles messages sent to the WebSocket group from Kafka.
        """
        message = event['message']
        await self.send(text_data=json.dumps(message))


class AuthenticatedWebsocketConsumer(BaseConsumer):
    """
    A WebSocket consumer that handles authentication using JWT tokens.
    Subclasses can still specify a group_name, or you can subclass this
    directly if you need per-route authentication.
    """

    async def connect(self):
        """
        Handles the WebSocket connection after validating the JWT token.
        """
        user = await self.authenticate_user()  # Validate JWT
        if user:
            self.scope['user'] = user
            await super().connect()  # Calls BaseConsumer.connect()
            logger.info(f"WebSocket connected for user: {user.username}")
        else:
            logger.warning("Authentication failed, rejecting connection.")
            await self.close()

    async def authenticate_user(self):
        """
        Validates the JWT token passed in the WebSocket query string (?token=...).
        """
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        token_list = params.get('token')

        if token_list:
            token = token_list[0]
            logger.info(f"Received token: {token[:10]}...")  # Partial logging for security

            try:
                UntypedToken(token)  # Validate the token format
                decoded = TokenBackend(
                    algorithm=settings.SIMPLE_JWT['ALGORITHM']
                ).decode(token, verify=True)

                logger.info(f"Decoded JWT Token: {decoded}")
                user = await self.get_user(decoded['user_id'])
                if user:
                    return user
                else:
                    logger.warning(f"User with ID {decoded['user_id']} not found.")
            except ExpiredSignatureError:
                logger.warning("Token has expired.")
                await self.send(text_data=json.dumps({'error': 'Token has expired.'}))
            except DecodeError as e:
                logger.warning(f"Token decoding error: {e}")
                await self.send(text_data=json.dumps({'error': 'Invalid token.'}))
            except (InvalidToken, TokenError) as e:
                logger.warning(f"Invalid token error: {e}")
                await self.send(text_data=json.dumps({'error': 'Invalid token.'}))
        else:
            logger.warning("Token not provided.")
            await self.send(text_data=json.dumps({'error': 'Token not provided.'}))

        # In all error cases, close the connection:
        await self.close()
        return None

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def receive(self, text_data):
        """
        Handle received WebSocket messages, log them, and respond.
        """
        logger.info(f"Received WebSocket message: {text_data}")
        try:
            data = json.loads(text_data)
            message = data.get('message', 'No message content')

            # Log the processed message
            logger.info(f"Processed message: {message}")

            # Echo the message back
            await self.send(text_data=json.dumps({'message': message}))
        except json.JSONDecodeError:
            logger.error("Received invalid JSON message.")
            await self.send(text_data=json.dumps({'error': 'Invalid JSON message received.'}))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({'error': 'Error processing message.'}))


#
# Specific Consumers With Fixed group_name
#

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


class NotificationConsumer(BaseConsumer):
    group_name = 'notifications'


class UserConsumer(AuthenticatedWebsocketConsumer):
    """
    Consumer that tracks user presence in the 'users' group.
    Inherits from AuthenticatedWebsocketConsumer to ensure token-based authentication.
    """

    group_name = 'users'

    async def connect(self):
        await super().connect()
        user = self.scope.get("user")
        self.user_id = user.id if user else None
        self.username = user.username if user else "Unknown"
        if self.user_id:
            await self.channel_layer.group_send(self.group_name, {
                'type': 'user_online',
                'user_id': self.user_id,
                'username': self.username,
            })

    async def disconnect(self, close_code):
        if self.user_id:
            await self.channel_layer.group_send(self.group_name, {
                'type': 'user_offline',
                'user_id': self.user_id,
                'username': self.username,
            })
        await super().disconnect(close_code)

    async def user_online(self, event):
        """
        A user came online. Update the cache and broadcast to group members.
        """
        user_id = event['user_id']
        username = event.get('username', '')
        await self.update_online_users_cache(user_id, online=True)
        await self.send(json.dumps({'type': 'user_online', 'user_id': user_id, 'username': username}))

    async def user_offline(self, event):
        """
        A user went offline. Update the cache and broadcast to group members.
        """
        user_id = event['user_id']
        username = event.get('username', '')
        await self.update_online_users_cache(user_id, online=False)
        await self.send(json.dumps({'type': 'user_offline', 'user_id': user_id, 'username': username}))

    @database_sync_to_async
    def update_online_users_cache(self, user_id, online=True):
        online_user_ids = cache.get('online_users', [])
        if online:
            if user_id not in online_user_ids:
                online_user_ids.append(user_id)
                logger.info(f"User {user_id} added to online users")
        else:
            if user_id in online_user_ids:
                online_user_ids.remove(user_id)
                logger.info(f"User {user_id} removed from online users")
        cache.set('online_users', online_user_ids, None)


class PresenceConsumer(AsyncWebsocketConsumer):
    """
    A simple consumer that doesn't need group_name logic from BaseConsumer.
    """
    async def connect(self):
        self.group_name = 'presence'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        # Echo it back
        await self.send(json.dumps({'message': message}))


class DefaultConsumer(AsyncWebsocketConsumer):
    """
    Default catch-all for /ws/ with no subpath.
    """
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({
            'message': 'Connected to the default WebSocket endpoint.'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
