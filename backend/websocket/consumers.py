# backend/websocket/consumers.py

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


class AuthenticatedWebsocketConsumer(AsyncWebsocketConsumer):
    """
    An authenticated WebSocket consumer that verifies JWT tokens.
    """

    async def connect(self):
        # Extract the group from the URL route
        self.group_name = self.scope['url_route']['kwargs'].get('group')

        # Extract the token from query parameters
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        token = params.get('token')

        if token:
            token = token[0]
            try:
                # Validate token
                UntypedToken(token)
                # Decode token to get user information
                decoded = TokenBackend(algorithm=settings.SIMPLE_JWT['ALGORITHM']).decode(token, verify=True)
                user = await self.get_user(decoded['user_id'])
                if user:
                    self.scope['user'] = user
                    # Add user to group
                    await self.channel_layer.group_add(
                        self.group_name,
                        self.channel_name
                    )
                    await self.accept()
                    logger.info(f"WebSocket connected for group: {self.group_name} by user: {user.username}")
                else:
                    logger.warning("WebSocket connection rejected: User not found.")
                    await self.close()
            except (InvalidToken, TokenError) as e:
                logger.warning(f"WebSocket connection rejected due to invalid token: {e}")
                await self.close()
        else:
            logger.warning("WebSocket connection rejected: No token provided.")
            await self.close()

    async def disconnect(self, close_code):
        # Remove user from group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from group: {self.group_name}")

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def kafka_message(self, event):
        """
        Handle messages sent to the WebSocket group from Kafka.
        """
        message = event['message']
        logger.debug(f"{self.__class__.__name__} received message: {message}")
        await self.send(text_data=json.dumps(message))


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
