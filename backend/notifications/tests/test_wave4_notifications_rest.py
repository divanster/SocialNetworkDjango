from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification

User = get_user_model()


class Wave4NotificationsRestTests(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            email='wave4-notif-sender@example.com',
            username='wave4_notif_sender',
            password='StrongPass123!',
        )
        self.receiver = User.objects.create_user(
            email='wave4-notif-receiver@example.com',
            username='wave4_notif_receiver',
            password='StrongPass123!',
        )
        self.other = User.objects.create_user(
            email='wave4-notif-other@example.com',
            username='wave4_notif_other',
            password='StrongPass123!',
        )
        self.notification = Notification.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            notification_type='message',
            text='new message',
        )
        self.client.force_authenticate(user=self.receiver)

    def test_list_and_unread_count(self):
        list_response = self.client.get('/api/v1/notifications/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)

        count_response = self.client.get('/api/v1/notifications/count/')
        self.assertEqual(count_response.status_code, status.HTTP_200_OK)
        self.assertEqual(count_response.data['count'], 1)

        action_count_response = self.client.get('/api/v1/notifications/unread_count/')
        self.assertEqual(action_count_response.status_code, status.HTTP_200_OK)
        self.assertEqual(action_count_response.data['count'], 1)

    def test_mark_one_read_and_mark_all_read(self):
        one_read = self.client.post(f'/api/v1/notifications/{self.notification.id}/mark_as_read/')
        self.assertEqual(one_read.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

        Notification.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            notification_type='comment',
            text='new comment',
        )
        all_read = self.client.post('/api/v1/notifications/mark_all_as_read/')
        self.assertEqual(all_read.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(receiver=self.receiver, is_read=False).count(), 0)

    def test_unauthorized_notification_access_rejected(self):
        self.client.force_authenticate(user=self.other)
        detail_response = self.client.get(f'/api/v1/notifications/{self.notification.id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)

        mark_response = self.client.post(f'/api/v1/notifications/{self.notification.id}/mark_as_read/')
        self.assertEqual(mark_response.status_code, status.HTTP_404_NOT_FOUND)
