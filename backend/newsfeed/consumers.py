import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from kafka_app.consumer import KafkaConsumerClient
import asyncio

logger = logging.getLogger(__name__)


class NewsfeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'newsfeed'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info('WebSocket connected')

        # Start consuming Kafka messages asynchronously
        self.consumer = KafkaConsumerClient('NEWSFEED_EVENTS')
        asyncio.create_task(self.consume_messages())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info('WebSocket disconnected')

    async def consume_messages(self):
        try:
            for message in self.consumer.consume_messages():
                await self.send(text_data=json.dumps(message))
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        logger.info(f'Received message: {data}')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'feed_message',
                'message': data['message']
            }
        )

    async def feed_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
        logger.info(f'Sent message: {message}')
