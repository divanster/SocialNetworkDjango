import json
from channels.generic.websocket import AsyncWebsocketConsumer
from kafka_app.consumer import KafkaConsumerClient
import asyncio
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Start consuming Kafka messages asynchronously
        self.consumer = KafkaConsumerClient('MESSENGER_EVENTS')
        asyncio.create_task(self.consume_messages())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        self.consumer.close()

    async def consume_messages(self):
        try:
            for message in self.consumer.consume_messages():
                await self.send(text_data=json.dumps(message))
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data['message']
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
