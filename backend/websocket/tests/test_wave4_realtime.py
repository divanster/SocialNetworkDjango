from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from config.asgi import application
from messenger.models import Message
from notifications.models import Notification

User = get_user_model()


class Wave4WebSocketAuthAndRealtimeTests(TransactionTestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email='wave4-ws-a@example.com',
            username='wave4_ws_a',
            password='StrongPass123!',
        )
        self.user_b = User.objects.create_user(
            email='wave4-ws-b@example.com',
            username='wave4_ws_b',
            password='StrongPass123!',
        )
        self.user_c = User.objects.create_user(
            email='wave4-ws-c@example.com',
            username='wave4_ws_c',
            password='StrongPass123!',
        )
        self.token_a = str(RefreshToken.for_user(self.user_a).access_token)
        self.token_b = str(RefreshToken.for_user(self.user_b).access_token)
        self.token_c = str(RefreshToken.for_user(self.user_c).access_token)
        self.ws_headers = [
            (b'origin', b'http://localhost:3002'),
            (b'host', b'localhost:3002'),
        ]

    def test_websocket_routing_and_auth(self):
        async def scenario():
            valid = WebsocketCommunicator(
                application,
                f"/ws/messenger/?token={self.token_a}",
                headers=self.ws_headers
            )
            connected, _ = await valid.connect()
            self.assertTrue(connected)
            await valid.disconnect()

            wrong_prefix = WebsocketCommunicator(
                application,
                f"/ws/ws/messenger/?token={self.token_a}",
                headers=self.ws_headers
            )
            connected_wrong, _ = await wrong_prefix.connect()
            self.assertFalse(connected_wrong)

            invalid = WebsocketCommunicator(
                application,
                "/ws/messenger/?token=invalid",
                headers=self.ws_headers
            )
            connected_invalid, _ = await invalid.connect()
            self.assertFalse(connected_invalid)

            missing = WebsocketCommunicator(
                application,
                "/ws/messenger/",
                headers=self.ws_headers
            )
            connected_missing, _ = await missing.connect()
            self.assertFalse(connected_missing)

        async_to_sync(scenario)()

    def test_messenger_realtime_delivery(self):
        async def scenario():
            receiver_socket = WebsocketCommunicator(
                application,
                f"/ws/messenger/?token={self.token_b}",
                headers=self.ws_headers
            )
            connected, _ = await receiver_socket.connect()
            self.assertTrue(connected)

            message = await database_sync_to_async(Message.objects.create)(
                sender=self.user_a,
                receiver=self.user_b,
                content='hello realtime',
            )
            payload = await receiver_socket.receive_json_from(timeout=2)
            self.assertEqual(payload.get('type'), 'messenger.message')
            self.assertEqual(payload.get('data', {}).get('id'), str(message.id))
            self.assertEqual(payload.get('data', {}).get('content'), 'hello realtime')
            await receiver_socket.disconnect()

        async_to_sync(scenario)()

    def test_notifications_realtime_delivery_isolated_to_target(self):
        async def scenario():
            target_socket = WebsocketCommunicator(
                application,
                f"/ws/notifications/?token={self.token_b}",
                headers=self.ws_headers
            )
            connected_target, _ = await target_socket.connect()
            self.assertTrue(connected_target)

            other_socket = WebsocketCommunicator(
                application,
                f"/ws/notifications/?token={self.token_c}",
                headers=self.ws_headers
            )
            connected_other, _ = await other_socket.connect()
            self.assertTrue(connected_other)

            notification = await database_sync_to_async(Notification.objects.create)(
                sender=self.user_a,
                receiver=self.user_b,
                notification_type='message',
                text='new message',
            )

            target_payload = await target_socket.receive_json_from(timeout=2)
            self.assertEqual(target_payload.get('type'), 'notification')
            self.assertEqual(target_payload.get('data', {}).get('id'), str(notification.id))

            got_other = await other_socket.receive_nothing(timeout=0.5)
            self.assertTrue(got_other)

            await target_socket.disconnect()
            await other_socket.disconnect()

        async_to_sync(scenario)()

    def test_presence_connect_disconnect(self):
        async def scenario():
            presence_socket = WebsocketCommunicator(
                application,
                f"/ws/presence/?token={self.token_a}",
                headers=self.ws_headers
            )
            connected, _ = await presence_socket.connect()
            self.assertTrue(connected)
            first_payload = await presence_socket.receive_json_from(timeout=2)
            self.assertEqual(first_payload.get('type'), 'user_online')
            self.assertEqual(first_payload.get('user_id'), str(self.user_a.id))
            await presence_socket.disconnect()

        async_to_sync(scenario)()

    def test_online_users_endpoint_works_without_redis(self):
        client = APIClient()
        client.force_authenticate(user=self.user_a)
        response = client.get('/api/v1/get_online_users/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('online_users', response.data)
