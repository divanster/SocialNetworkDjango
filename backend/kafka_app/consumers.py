import os
import json
import logging
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.conf import settings
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope['query_string'].decode().split('=')[1]

        try:
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'],
                                 algorithms=['HS256'])
            user_id = payload.get('user_id')

            if user_id is None:
                raise ValueError("User ID missing from token.")

            self.user = await self.get_user(user_id)
            if self.user is None:
                raise ValueError("User not found.")

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            await self.close()
            return

        self.group_name = self.scope['url_route']['kwargs']['group_name']
        if not self.group_name:
            logger.warning("WebSocket connection attempt without group name.")
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected and joined group: {self.group_name}")

    async def get_user(self, user_id):
        try:
            user = await database_sync_to_async(get_user_model().objects.get)(
                id=user_id)
            return user
        except get_user_model().DoesNotExist:
            return None
