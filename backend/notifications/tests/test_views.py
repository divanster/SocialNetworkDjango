from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class NotificationViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.sender = User.objects.create_user(username='sender', email='sender@example.com', password='password123')
        self.receiver = User.objects.create_user(username='receiver', email='receiver@example.com', password='password123')
        self.client.force_authenticate(user=self.sender)
        self.notification_data = {
            "sender_id": self.sender.id,
            "sender_username": self.sender.username,
            "receiver_id": self.receiver.id,
            "receiver_username": self.receiver.username,
            "notification_type": "like",
            "text": "You have a new like!"
        }

    def test_create_notification(self):
        response = self.client.post(reverse('notification-list'), self.notification_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.get()
        self.assertEqual(notification.text, 'You have a new like!')

    def test_list_notifications(self):
        Notification.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            notification_type="follow"
        )
        response = self.client.get(reverse('notification-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mark_notification_as_read(self):
        notification = Notification.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            notification_type="follow"
        )
        url = reverse('notification-detail', kwargs={'pk': notification.pk})
        response = self.client.patch(url, {"is_read": True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_delete_notification(self):
        notification = Notification.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            notification_type="comment"
        )
        url = reverse('notification-detail', kwargs={'pk': notification.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 0)
