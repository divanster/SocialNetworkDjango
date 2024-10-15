from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class NotificationSignalsTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', email='sender@example.com', password='password123')
        self.receiver = User.objects.create_user(username='receiver', email='receiver@example.com', password='password123')

    @patch('notifications.tasks.send_notification_event_to_kafka.delay')
    def test_notification_created_signal(self, mock_send_notification_event_to_kafka):
        notification = Notification.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            notification_type='follow'
        )
        mock_send_notification_event_to_kafka.assert_called_once_with(notification.id, 'created')

    @patch('notifications.tasks.send_notification_event_to_kafka.delay')
    def test_notification_deleted_signal(self, mock_send_notification_event_to_kafka):
        notification = Notification.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            notification_type='follow'
        )
        notification.delete()
        mock_send_notification_event_to_kafka.assert_called_with(notification.id, 'deleted')
