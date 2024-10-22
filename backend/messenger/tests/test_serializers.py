from rest_framework import serializers
from rest_framework.test import APITestCase
from messenger.serializers import MessageSerializer
from messenger.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializerTestCase(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(email='sender@example.com',
                                               username='sender',
                                               password='password123')
        self.receiver = User.objects.create_user(email='receiver@example.com',
                                                 username='receiver',
                                                 password='password123')

    def test_message_serialization(self):
        """
        Test the serialization of a Message instance.
        """
        # Create a message instance
        message = Message.objects.create(
            sender_id=self.sender.id,
            sender_username=self.sender.username,
            receiver_id=self.receiver.id,
            receiver_username=self.receiver.username,
            content='Serialized message content'
        )

        # Serialize the message instance
        serializer = MessageSerializer(message)
        expected_data = {
            'id': str(message.id),  # Assuming `id` is a UUIDField (needs to be cast to str)
            'sender': message.sender_id,
            'receiver': message.receiver_id,
            'sender_name': message.sender_username,
            'receiver_name': message.receiver_username,
            'content': 'Serialized message content',
            'timestamp': serializers.DateTimeField().to_representation(message.timestamp),
            'is_read': message.is_read
        }

        # Assert that serialized data matches expected values
        self.assertEqual(serializer.data, expected_data)

    def test_message_deserialization(self):
        """
        Test the deserialization of a valid Message instance from data.
        """
        data = {
            'sender': self.sender.id,
            'receiver': self.receiver.id,
            'content': 'New message content'
        }

        # Deserialize the data to validate and create a Message instance
        serializer = MessageSerializer(data=data)

        # Serializer should be valid with correct input data
        self.assertTrue(serializer.is_valid())
        message_instance = serializer.save()

        # Assert the message was created correctly
        self.assertEqual(message_instance.sender_id, self.sender.id)
        self.assertEqual(message_instance.receiver_id, self.receiver.id)
        self.assertEqual(message_instance.content, 'New message content')

    def test_invalid_message_data(self):
        """
        Test the validation fails for message creation with empty content.
        """
        data = {
            'sender': self.sender.id,
            'receiver': self.receiver.id,
            'content': ''  # Invalid as content should not be empty
        }

        # Deserialize and validate the data
        serializer = MessageSerializer(data=data)

        # Serializer should not be valid with empty content
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)

    def test_missing_receiver_field(self):
        """
        Test validation fails for message creation without receiver data.
        """
        data = {
            'sender': self.sender.id,
            'content': 'This message has no receiver'
        }

        serializer = MessageSerializer(data=data)

        # Serializer should not be valid as receiver is missing
        self.assertFalse(serializer.is_valid())
        self.assertIn('receiver', serializer.errors)

    def test_missing_sender_field(self):
        """
        Test validation fails for message creation without sender data.
        """
        data = {
            'receiver': self.receiver.id,
            'content': 'This message has no sender'
        }

        serializer = MessageSerializer(data=data)

        # Serializer should not be valid as sender is missing
        self.assertFalse(serializer.is_valid())
        self.assertIn('sender', serializer.errors)
