from django.test import TestCase
from unittest.mock import patch
from messenger.models import Message
from django.contrib.auth import get_user_model
from django.utils import timezone

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
        """
        Test that a Kafka message is sent when a new message is created.
        """
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='Test Message Content'
        )

        # Assert that KafkaProducerClient.send_message was called once
        mock_send_message.assert_called_once()

        # Assert that the correct message was sent to Kafka
        expected_message = {
            "message_id": str(message.id),
            "content": message.content,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "timestamp": message.timestamp.isoformat(),
            "event": "created"
        }
        mock_send_message.assert_called_with('MESSENGER_EVENTS', expected_message)

    @patch('messenger.signals.KafkaProducerClient.send_message')
    def test_message_deleted_signal(self, mock_send_message):
        """
        Test that a Kafka message is sent when a message is deleted.
        """
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='Test Message Content'
        )
        message_id = message.id

        # Delete the message
        message.delete()

        # Assert that KafkaProducerClient.send_message was called once
        mock_send_message.assert_called_once()

        # Assert that the correct message was sent to Kafka
        expected_message = {
            "message_id": str(message_id),
            "action": "deleted"
        }
        mock_send_message.assert_called_with('MESSENGER_EVENTS', expected_message)
