from django.test import TestCase
from unittest.mock import patch
from messenger.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSignalsTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(email='sender@example.com',
                                               username='sender',
                                               password='password123')
        self.receiver = User.objects.create_user(email='receiver@example.com',
                                                 username='receiver',
                                                 password='password123')

    @patch('messenger.signals.KafkaProducerClient.send_message')
    def test_message_created_signal(self, mock_send_message):
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='Test Message Content'
        )
        mock_send_message.assert_called_once()

    @patch('messenger.signals.KafkaProducerClient.send_message')
    def test_message_deleted_signal(self, mock_send_message):
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='Test Message Content'
        )
        message.delete()
        mock_send_message.assert_called_once()
