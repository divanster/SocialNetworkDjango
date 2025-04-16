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
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"Connected to group {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"Disconnected from group {self.group_name}")

    # Crucially, add this method explicitly:
    async def kafka_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "event": message.get("event", "kafka_event"),
            "data": message.get("data", {})
        }))
        logger.info(f"WebSocket sent kafka_message: {message}")
