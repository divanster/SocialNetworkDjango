from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from messenger.models import Message
from unittest.mock import patch

User = get_user_model()


class MessageViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.sender = User.objects.create_user(email='sender@example.com',
                                               username='sender',
                                               password='password123')
        self.receiver = User.objects.create_user(email='receiver@example.com',
                                                 username='receiver',
                                                 password='password123')
        self.client.force_authenticate(user=self.sender)

    @patch('messenger.views.KafkaProducerClient.send_message')
    def test_create_message(self, mock_send_message):
        url = reverse('message-list')
        data = {
            'receiver': self.receiver.id,
            'content': 'This is a new message'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send_message.assert_called_once()

    def test_list_messages(self):
        Message.objects.create(sender_id=self.sender.id,
                               sender_username=self.sender.username,
                               receiver_id=self.receiver.id,
                               receiver_username=self.receiver.username,
                               content='Test Message 1')
        Message.objects.create(sender_id=self.sender.id,
                               sender_username=self.sender.username,
                               receiver_id=self.receiver.id,
                               receiver_username=self.receiver.username,
                               content='Test Message 2')
        url = reverse('message-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_messages_count(self):
        Message.objects.create(sender_id=self.sender.id,
                               sender_username=self.sender.username,
                               receiver_id=self.receiver.id,
                               receiver_username=self.receiver.username,
                               content='Unread Message', is_read=False)
        url = reverse('messenger:messages-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
