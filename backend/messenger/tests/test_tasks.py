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
    def test_send_message_event_to_kafka(self, mock_send_message):
        send_message_event_to_kafka(self.message.id, 'created')
        mock_send_message.assert_called_once()
