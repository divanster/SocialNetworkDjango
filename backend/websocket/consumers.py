# backend/websocket/consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'posts'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"PostConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class AlbumConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'albums'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"AlbumConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


# Similarly, implement other consumers for each app

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'comments'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"CommentConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class FollowConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'follows'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"FollowConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class FriendConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'friends'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"FriendConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class MessengerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'messenger'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"MessengerConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class NewsfeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'newsfeed'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"NewsfeedConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class ReactionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'reactions'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"ReactionConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class SocialConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'social'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"SocialConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class StoryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'stories'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"StoryConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class TaggingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'tagging'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"TaggingConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'users'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"UserConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'notifications'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected for group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    async def kafka_message(self, event):
        message = event['message']
        logger.debug(f"NotificationConsumer received message: {message}")
        await self.send(text_data=json.dumps(message))
