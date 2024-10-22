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
        """
        Test creating a new message.
        """
        url = reverse('message-list')
        data = {
            'receiver': self.receiver.id,
            'content': 'This is a new message'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

        # Check if the message has been created with correct content
        message = Message.objects.first()
        self.assertEqual(message.content, 'This is a new message')
        self.assertEqual(message.sender_id, self.sender.id)
        self.assertEqual(message.receiver_id, self.receiver.id)

        # Verify Kafka producer client was called
        mock_send_message.assert_called_once()

    def test_list_messages(self):
        """
        Test listing all messages for the authenticated user.
        """
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
        self.assertEqual(response.data[0]['content'], 'Test Message 1')
        self.assertEqual(response.data[1]['content'], 'Test Message 2')

    def test_retrieve_message(self):
        """
        Test retrieving a specific message by its ID.
        """
        message = Message.objects.create(sender_id=self.sender.id,
                                         sender_username=self.sender.username,
                                         receiver_id=self.receiver.id,
                                         receiver_username=self.receiver.username,
                                         content='Test Message Content')
        url = reverse('message-detail', kwargs={'pk': message.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test Message Content')
        self.assertEqual(response.data['sender'], self.sender.id)
        self.assertEqual(response.data['receiver'], self.receiver.id)

    def test_delete_message(self):
        """
        Test deleting a message.
        """
        message = Message.objects.create(sender_id=self.sender.id,
                                         sender_username=self.sender.username,
                                         receiver_id=self.receiver.id,
                                         receiver_username=self.receiver.username,
                                         content='Message to be deleted')
        url = reverse('message-detail', kwargs={'pk': message.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Message.objects.count(), 0)

    def test_messages_count(self):
        """
        Test retrieving the count of unread messages for the authenticated user.
        """
        Message.objects.create(sender_id=self.sender.id,
                               sender_username=self.sender.username,
                               receiver_id=self.receiver.id,
                               receiver_username=self.receiver.username,
                               content='Unread Message', is_read=False)
        url = reverse('messenger:messages-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    @patch('messenger.views.KafkaProducerClient.send_message')
    def test_update_message(self, mock_send_message):
        """
        Test updating the content of a message.
        """
        message = Message.objects.create(sender_id=self.sender.id,
                                         sender_username=self.sender.username,
                                         receiver_id=self.receiver.id,
                                         receiver_username=self.receiver.username,
                                         content='Old Message Content')
        url = reverse('message-detail', kwargs={'pk': message.pk})
        data = {
            'content': 'Updated Message Content'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh message instance from the database
        message.refresh_from_db()
        self.assertEqual(message.content, 'Updated Message Content')

        # Verify Kafka producer client was called
        mock_send_message.assert_called_once()

