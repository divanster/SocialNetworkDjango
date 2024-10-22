from django.test import TestCase
from messenger.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageModelTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@example.com', username='sender', password='password123')
        self.receiver = User.objects.create_user(
            email='receiver@example.com', username='receiver', password='password123')

    def test_create_message(self):
        # Create a message from sender to receiver
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='Hello, this is a message.'
        )
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.content, 'Hello, this is a message.')
        self.assertFalse(message.is_read)  # Check if message is unread by default

    def test_str_method(self):
        # Test the string representation of a message
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='A short message for testing purposes.'
        )
        self.assertEqual(str(message), 'sender -> receiver: A short message fo')

    def test_mark_as_read(self):
        # Test the mark_as_read method of the Message model
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='This message will be marked as read.'
        )
        self.assertFalse(message.is_read)  # Message should be unread initially
        message.mark_as_read()
        message.refresh_from_db()  # Reload the message from the database
        self.assertTrue(message.is_read)  # Message should now be marked as read

    def test_create_message_without_receiver(self):
        # Test creating a message without specifying a receiver (e.g., for a group)
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            content='This is a broadcast message.'
        )
        self.assertEqual(Message.objects.count(), 1)
        self.assertIsNone(message.receiver_id)
        self.assertEqual(message.content, 'This is a broadcast message.')

    def test_create_message_with_empty_content(self):
        # Test creating a message with empty content should fail validation
        with self.assertRaises(ValueError):
            Message.objects.create(
                sender_id=self.sender.id,
                sender_username=self.sender.username,
                receiver_id=self.receiver.id,
                receiver_username=self.receiver.username,
                content=''
            )

    def test_message_is_read_default(self):
        # Test that the `is_read` field defaults to False
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='Testing is_read default value.'
        )
        self.assertFalse(message.is_read)  # Ensure the message starts as unread
