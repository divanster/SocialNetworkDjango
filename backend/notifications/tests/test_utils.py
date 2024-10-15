# backend/notifications/tests/test_utils.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.utils import create_notification
from channels.layers import get_channel_layer
from unittest.mock import patch

User = get_user_model()


class CreateNotificationUtilsTest(TestCase):

    def setUp(self):
        self.actor = User.objects.create_user(
            username="actor_user", email="actor@example.com", password="password"
        )
        self.recipient = User.objects.create_user(
            username="recipient_user", email="recipient@example.com",
            password="password"
        )

    @patch('channels.layers.get_channel_layer')
    def test_create_notification_success(self, mock_get_channel_layer):
        # Mocking the get_channel_layer to prevent actual WebSocket calls
        mock_channel_layer = mock_get_channel_layer.return_value
        mock_group_send = patch('asgiref.sync.async_to_sync').start()

        # Call create_notification function
        create_notification(
            recipient=self.recipient, actor=self.actor, verb="liked", target=None
        )

        # Ensure notification was created in the database
        notification = Notification.objects.get(recipient=self.recipient)
        self.assertIsNotNone(notification)
        self.assertEqual(notification.sender_id, self.actor.id)
        self.assertEqual(notification.receiver_id, self.recipient.id)
        self.assertEqual(notification.notification_type, 'liked')

        # Ensure that the WebSocket message is properly sent
        mock_group_send.assert_called_once_with(
            f'notifications_{self.recipient.id}',
            {
                'type': 'notify',
                'content': {
                    'recipient': self.recipient.id,
                    'actor': self.actor.username,
                    'verb': 'liked',
                    'target': None,
                }
            }
        )
