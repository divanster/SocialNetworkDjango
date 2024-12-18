# kafka_app/consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        if not self.group_name:
            logger.warning("WebSocket connection attempt without group name.")
            await self.close()
            return

        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected and joined group: {self.group_name}")

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected and left group: {self.group_name}")

    async def kafka_message(self, event):
        # Send message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps(message))
        logger.info(f"Sent message to WebSocket group {self.group_name}: {message}")
