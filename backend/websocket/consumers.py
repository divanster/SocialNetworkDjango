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
    Base WebSocket consumer that handles joining/leaving a group.
    Subclasses set a class-level group_name to identify which group to join.
    """
    group_name = None

    async def connect(self):
        if not self.group_name:
            self.group_name = "default"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def kafka_message(self, event):
        message = event["message"]
        await self.send(json.dumps(message))


class AuthenticatedWebsocketConsumer(BaseConsumer):
    """
    A WebSocket consumer that requires a valid JWT token in ?token=...
    If valid, self.scope['user'] is set to the matching User.
    """
    async def connect(self):
        user = await self.authenticate_user()
        if user:
            self.scope["user"] = user
            await super().connect()
            logger.info(f"WebSocket connected for user: {user.username}")
        else:
            logger.warning("Authentication failed, rejecting connection.")
            await self.close()

    async def authenticate_user(self):
        query_string = self.scope["query_string"].decode()
        params = parse_qs(query_string)
        token_list = params.get("token")
        if not token_list:
            logger.warning("Token not provided in query string.")
            await self.send(json.dumps({"error": "Token not provided."}))
            await self.close()
            return None
        token = token_list[0]
        logger.info(f"Received token: {token[:10]}...")  # Partial logging for security
        try:
            UntypedToken(token)
            # Pass the signing_key explicitly so a string is used.
            decoded = TokenBackend(
                algorithm=settings.SIMPLE_JWT["ALGORITHM"],
                signing_key=settings.SIMPLE_JWT["SIGNING_KEY"]
            ).decode(token, verify=True)
            logger.info(f"Decoded JWT Token: {decoded}")
            user = await self.get_user(decoded["user_id"])
            if user:
                return user
            else:
                logger.warning(f"User with ID {decoded['user_id']} not found.")
        except ExpiredSignatureError:
            logger.warning("Token has expired.")
            await self.send(json.dumps({"error": "Token has expired."}))
        except DecodeError as e:
            logger.warning(f"Token decoding error: {e}")
            await self.send(json.dumps({"error": "Invalid token."}))
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Invalid token error: {e}")
            await self.send(json.dumps({"error": "Invalid token."}))
        await self.close()
        return None

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def receive(self, text_data):
        logger.info(f"Received WebSocket message: {text_data}")
        try:
            data = json.loads(text_data)
            message = data.get("message", "No message content")
            logger.info(f"Processed message: {message}")
            await self.send(json.dumps({"message": message}))
        except json.JSONDecodeError:
            logger.error("Invalid JSON message.")
            await self.send(json.dumps({"error": "Invalid JSON message."}))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(json.dumps({"error": "Error processing message."}))


# Specific Consumers

class PostConsumer(BaseConsumer):
    group_name = "posts"


class AlbumConsumer(BaseConsumer):
    group_name = "albums"


class CommentConsumer(BaseConsumer):
    group_name = "comments"


class FollowConsumer(BaseConsumer):
    group_name = "follows"


class FriendConsumer(BaseConsumer):
    group_name = "friends"


class MessengerConsumer(BaseConsumer):
    group_name = "messenger"


class NewsfeedConsumer(BaseConsumer):
    group_name = "newsfeed"


class ReactionConsumer(BaseConsumer):
    group_name = "reactions"


class SocialConsumer(BaseConsumer):
    group_name = "social"


class StoryConsumer(BaseConsumer):
    group_name = "stories"


class TaggingConsumer(BaseConsumer):
    group_name = "tagging"


class NotificationConsumer(BaseConsumer):
    group_name = "notifications"


class UserConsumer(AuthenticatedWebsocketConsumer):
    """
    Tracks user presence in the 'users' group.
    Broadcasts 'user_online'/'user_offline' events with user_id and username.
    """
    group_name = "users"

    async def connect(self):
        await super().connect()
        user = self.scope.get("user")
        # Convert user_id to string to avoid serialization issues with UUIDs.
        self.user_id = str(user.id) if user else None
        self.username = user.username if user else "Unknown"
        if self.user_id:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "user_online",
                    "user_id": self.user_id,
                    "username": self.username,
                },
            )

    async def disconnect(self, close_code):
        if self.user_id:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "user_offline",
                    "user_id": self.user_id,
                    "username": self.username,
                },
            )
        await super().disconnect(close_code)

    async def user_online(self, event):
        user_id = event["user_id"]
        username = event.get("username", "")
        await self.update_online_users_cache(user_id, online=True)
        await self.send(json.dumps({
            "group": "users",
            "message": {
                "type": "user_online",
                "user_id": user_id,
                "username": username,
            }
        }))

    async def user_offline(self, event):
        user_id = event["user_id"]
        username = event.get("username", "")
        await self.update_online_users_cache(user_id, online=False)
        await self.send(json.dumps({
            "group": "users",
            "message": {
                "type": "user_offline",
                "user_id": user_id,
                "username": username,
            }
        }))

    @database_sync_to_async
    def update_online_users_cache(self, user_id, online=True):
        online_user_ids = cache.get("online_users", [])
        if online:
            if user_id not in online_user_ids:
                online_user_ids.append(user_id)
                logger.info(f"User {user_id} added to online users")
        else:
            if user_id in online_user_ids:
                online_user_ids.remove(user_id)
                logger.info(f"User {user_id} removed from online users")
        cache.set("online_users", online_user_ids, None)


class PresenceConsumer(AsyncWebsocketConsumer):
    """
    A simple consumer that doesn't require auth.
    """
    async def connect(self):
        self.group_name = "presence"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        await self.send(json.dumps({"message": message}))


class DefaultConsumer(AsyncWebsocketConsumer):
    """
    Catch-all for /ws/ with no subpath. Remove if not needed.
    """
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({"message": "Connected to default endpoint."}))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
