from django.test import TestCase
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class NotificationModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', email='sender@example.com', password='password123')
        self.receiver = User.objects.create_user(username='receiver', email='receiver@example.com', password='password123')

    def test_notification_creation(self):
        notification = Notification.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            notification_type='like',
            text='Test notification'
        )
        self.assertEqual(str(notification), f"{self.sender.username} sent a Like notification to {self.receiver.username}")
        self.assertEqual(notification.notification_type, 'like')
        self.assertFalse(notification.is_read)

    def test_mark_as_read(self):
        notification = Notification.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            notification_type='comment',
            text='Another test notification'
        )
        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        self.assertTrue(notification.is_read)
