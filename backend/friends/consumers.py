# backend/friends/consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from kafka_app.consumer import KafkaConsumerClient

logger = logging.getLogger(__name__)


class FriendRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = f'friend_requests_{self.scope["user"].id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Consume Kafka messages and send to WebSocket clients
        consumer = KafkaConsumerClient('FRIEND_EVENTS')
        for message in consumer.consume_messages():
            await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'friend_request_message',
                'message': data['message']
            }
        )

    async def friend_request_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
