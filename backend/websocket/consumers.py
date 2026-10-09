import asyncio
import json
import logging

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from django_redis import get_redis_connection
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)
REDIS_KEY = "online_users"
CACHE_KEY = "online_users_fallback"


class BaseConsumer(AsyncWebsocketConsumer):
    group_name = None

    async def connect(self):
        if not self.group_name:
            self.group_name = "default"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def kafka_message(self, event):
        await self.send(json.dumps(event.get("message", {}), default=str))


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


class MessengerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4000)
            return

        self.user_id = str(user.id)
        self.group_name = f"messenger_{self.user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # The server does not accept client-originated chat payloads over this socket.
        # Messages are persisted via REST and emitted to the receiver from signals.
        return

    async def messenger_event(self, event):
        await self.send(json.dumps({
            "type": "messenger.message",
            "data": event.get("payload", {}),
        }, default=str))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4000)
            return

        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        await self.send(json.dumps({
            "type": event.get("event", "notification"),
            "data": event.get("payload", {}),
        }, default=str))


class UserConsumer(AsyncWebsocketConsumer):
    group_name = "presence"

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4000)
            return

        self.user_id = str(user.id)
        self.username = user.username

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self._set_online(True)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "user_online",
                "user_id": self.user_id,
                "username": self.username,
            }
        )
        self.ping_task = asyncio.create_task(self._ping_loop())

    async def disconnect(self, close_code):
        if hasattr(self, "ping_task"):
            self.ping_task.cancel()

        await self._set_online(False)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "user_offline",
                "user_id": self.user_id,
                "username": self.username,
            }
        )

    async def user_online(self, event):
        await self.send(json.dumps(event, default=str))

    async def user_offline(self, event):
        await self.send(json.dumps(event, default=str))

    async def receive(self, text_data=None, bytes_data=None):
        if text_data == "ping":
            await self.send("pong")

    async def _ping_loop(self):
        while True:
            await asyncio.sleep(30)
            try:
                await self.send(text_data="ping")
            except Exception:
                break

    @sync_to_async
    def _set_online(self, online):
        try:
            redis_conn = get_redis_connection("default")
            if online:
                redis_conn.sadd(REDIS_KEY, self.user_id)
            else:
                redis_conn.srem(REDIS_KEY, self.user_id)
            redis_conn.expire(REDIS_KEY, 86400)
            return
        except (RedisError, NotImplementedError):
            pass

        cached = cache.get(CACHE_KEY, [])
        current = set(cached)
        if online:
            current.add(self.user_id)
        else:
            current.discard(self.user_id)
        cache.set(CACHE_KEY, list(current), timeout=86400)


class DefaultConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.close(code=4404)
