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
from django_redis import get_redis_connection

from django.core.cache import cache

logger = logging.getLogger(__name__)
User = get_user_model()


class BaseConsumer(AsyncWebsocketConsumer):
    """
    Base WebSocket consumer that handles joining and leaving a group.
    Subclasses set a class-level group_name to determine which group to join.
    """
    group_name = None

    async def connect(self):
        if not self.group_name:
            self.group_name = "default"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"Connected to group '{self.group_name}' on channel {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"Disconnected from group '{self.group_name}' on channel {self.channel_name} with code {close_code}")

    async def kafka_message(self, event):
        message = event["message"]
        await self.send(json.dumps(message))


class AuthenticatedWebsocketConsumer(BaseConsumer):
    """
    A WebSocket consumer that requires a valid JWT token in the query string (?token=...).
    If valid, sets self.scope['user'] to the corresponding User.
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


class MessengerConsumer(AsyncWebsocketConsumer):
    """
    A consumer that puts all connected clients in the 'messenger' group.
    It expects a JSON payload with a key "message" and then broadcasts this
    message to all clients in the group.
    """
    group_name = "messenger"

    async def connect(self):
        # Add this socket to the messenger group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"Connected to group '{self.group_name}' on channel {self.channel_name}")

    async def disconnect(self, close_code):
        # Remove this socket from the messenger group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"Disconnected from group '{self.group_name}' on channel {self.channel_name} (code {close_code})")

    async def receive(self, text_data):
        """
        When a message is received from the client, expect it in the form:
          { "message": { "content": "Hello", "sender_id": "..." } }
        and broadcast it to the messenger group.
        """
        logger.info(f"MessengerConsumer receive: {text_data}")
        try:
            data = json.loads(text_data)
            msg_obj = data.get("message")
            if msg_obj:
                await self.channel_layer.group_send(
                    self.group_name,  # Broadcast to the messenger group
                    {
                        "type": "messenger_message",  # Calls the messenger_message handler
                        "message": msg_obj,
                    }
                )
            else:
                logger.warning("No 'message' key in received data")
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in MessengerConsumer")
            await self.send(json.dumps({"error": "Invalid JSON"}))
        except Exception as e:
            logger.exception("Error in MessengerConsumer.receive")
            await self.send(json.dumps({"error": str(e)}))

    async def messenger_message(self, event):
        """
        Handler for the broadcast event.
        It sends the event to the client in the form:
          { "message": { ... } }
        """
        msg_obj = event.get("message")
        response = {
            "message": msg_obj
        }
        await self.send(json.dumps(response))


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


class NotificationConsumer(AuthenticatedWebsocketConsumer):
    """
    Per-user notifications.
    Clients connect to:
      ws://<host>/ws/notifications/?token=<access_token>
    After handshake, this consumer joins the group "user_<user_id>"
    and will receive every new Notification via its notify() handler.
    """

    async def connect(self):
        # Authenticate, then set dynamic group and join it
        user = await self.authenticate_user()
        if not user:
            return await self.close()
        self.scope["user"] = user
        self.group_name = f"user_{user.id}"
        await super().connect()  # BaseConsumer.connect() will group_add & accept()

    async def disconnect(self, close_code):
        # Clean up
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await super().disconnect(close_code)

    async def notify(self, event):
        """
        Called by your post_save signal via:
          channel_layer.group_send("user_<id>", { "type":"notify", ... })
        """
        await self.send(json.dumps({
            "type": event["event"],    # e.g. "notification"
            "data": event["payload"],  # serialized Notification instance
        }))



class UserConsumer(AuthenticatedWebsocketConsumer):
    """
    Tracks user presence in the 'users' group.
    Broadcasts 'user_online' and 'user_offline' events with user_id and username.
    """
    group_name = "users"

    async def connect(self):
        await super().connect()
        user = self.scope.get("user")
        self.user_id = str(user.id) if user else None
        self.username = user.username if user else "Unknown"
        if self.user_id:
            # Join the per-user group for individual notifications
            await self.channel_layer.group_add(f"user_{self.user_id}", self.channel_name)
            # Update online status: call the decorated function directly
            await self.update_online_users_cache(self.user_id, online=True)
            # Broadcast the online event to the entire 'users' group
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "user_online", "user_id": self.user_id, "username": self.username},
            )
            logger.info(f"Broadcasted user_online for {self.user_id}")
        # (The connection is already accepted in the parent.)

    async def disconnect(self, close_code):
        if self.user_id:
            # Leave the per-user group
            await self.channel_layer.group_discard(f"user_{self.user_id}", self.channel_name)
            # Update online status and remove from Redis
            await self.update_online_users_cache(self.user_id, online=False)
            # Broadcast the offline event
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "user_offline", "user_id": self.user_id, "username": self.username},
            )
            logger.info(f"Broadcasted user_offline for {self.user_id}")
        await super().disconnect(close_code)

    async def force_disconnect(self, event):
        logger.info(f"Force disconnect received for user {self.user_id}")
        await self.update_online_users_cache(self.user_id, online=False)
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "user_offline", "user_id": self.user_id, "username": self.username},
        )
        await self.close()

    @database_sync_to_async
    def update_online_users_cache(self, user_id, online=True):
        redis_conn = get_redis_connection("default")
        user_id_str = str(user_id)
        if online:
            redis_conn.sadd("online_users", user_id_str)
            current = redis_conn.smembers("online_users")
            logger.info(f"User {user_id_str} added. Online set now: {[uid.decode('utf-8') for uid in current]}")
        else:
            redis_conn.srem("online_users", user_id_str)
            current = redis_conn.smembers("online_users")
            logger.info(f"User {user_id_str} removed. Online set now: {[uid.decode('utf-8') for uid in current]}")

    # --- New Handlers Below ---
    async def user_online(self, event):
        """
        Handler for group messages with type "user_online".
        This forwards the event as a JSON object to the WebSocket client.
        """
        await self.send(json.dumps({
            "event": "user_online",
            "user_id": event["user_id"],
            "username": event["username"],
        }))

    async def user_offline(self, event):
        """
        Handler for group messages with type "user_offline".
        This forwards the event as a JSON object to the WebSocket client.
        """
        await self.send(json.dumps({
            "event": "user_offline",
            "user_id": event["user_id"],
            "username": event["username"],
        }))


class PresenceConsumer(AsyncWebsocketConsumer):
    """
    A simple consumer that does not require authentication.
    Used for testing or lightweight presence interactions.
    """
    async def connect(self):
        self.group_name = "presence"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("PresenceConsumer connected.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info("PresenceConsumer disconnected.")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        await self.send(json.dumps({"message": message}))


class DefaultConsumer(AsyncWebsocketConsumer):
    """
    Catch-all consumer for /ws/ endpoints with no subpath. Remove if not needed.
    """
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({"message": "Connected to default endpoint."}))
        logger.info("DefaultConsumer connected.")

    async def disconnect(self, close_code):
        logger.info(f"DefaultConsumer disconnected with code {close_code}.")

    async def receive(self, text_data):
        pass
