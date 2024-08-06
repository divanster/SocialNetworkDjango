import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'posts'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', None)
            if message is None:
                raise ValueError("No 'message' key in data")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'post_message',
                    'message': message
                }
            )
        except json.JSONDecodeError as e:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON',
                'details': str(e)
            }))
            await self.close(code=4000)
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': 'Internal Server Error',
                'details': str(e)
            }))
            await self.close(code=1011)

    async def post_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
