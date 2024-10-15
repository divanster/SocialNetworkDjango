from django.test import TestCase
from messenger.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageModelTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(email='sender@example.com',
                                               username='sender',
                                               password='password123')
        self.receiver = User.objects.create_user(email='receiver@example.com',
                                                 username='receiver',
                                                 password='password123')

    def test_create_message(self):
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='Hello, this is a message.'
        )
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.content, 'Hello, this is a message.')

    def test_str_method(self):
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='A short message for testing purposes.'
        )
        self.assertEqual(str(message), 'sender -> receiver: A short message fo')
