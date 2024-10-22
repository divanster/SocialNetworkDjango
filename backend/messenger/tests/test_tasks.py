from django.test import TestCase
from unittest.mock import patch
from messenger.models import Message
from messenger.tasks import send_message_event_to_kafka
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageTasksTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(email='sender@example.com',
                                               username='sender',
                                               password='password123')
        self.receiver = User.objects.create_user(email='receiver@example.com',
                                                 username='receiver',
                                                 password='password123')
        self.message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='Task Message Content'
        )

    @patch('messenger.tasks.KafkaProducerClient.send_message')
    def test_send_message_event_to_kafka_created(self, mock_send_message):
        """
        Test that a Kafka message is sent for a 'created' event.
        """
        send_message_event_to_kafka(self.message.id, 'created')

        expected_message = {
            "message_id": str(self.message.id),
            "content": self.message.content,
            "sender_id": self.message.sender_id,
            "receiver_id": self.message.receiver_id,
            "timestamp": self.message.timestamp.isoformat(),
            "event": "created"
        }

        # Check that the send_message method was called with the expected message content
        mock_send_message.assert_called_once_with('MESSENGER_EVENTS', expected_message)

    @patch('messenger.tasks.KafkaProducerClient.send_message')
    def test_send_message_event_to_kafka_deleted(self, mock_send_message):
        """
        Test that a Kafka message is sent for a 'deleted' event.
        """
        # Call the task for a deleted event
        send_message_event_to_kafka(self.message.id, 'deleted')

        expected_message = {
            "message_id": str(self.message.id),
            "action": "deleted"
        }

        # Check that the send_message method was called with the expected message content
        mock_send_message.assert_called_once_with('MESSENGER_EVENTS', expected_message)
