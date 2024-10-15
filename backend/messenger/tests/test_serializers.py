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
            'id': message.id,
            'sender': message.sender_id,
            'receiver': message.receiver_id,
            'sender_name': message.sender_username,
            'receiver_name': message.receiver_username,
            'content': 'Serialized message content',
            'timestamp': serializers.DateTimeField().to_representation(
                message.timestamp),
            'is_read': message.is_read
        }

        self.assertEqual(serializer.data, expected_data)

    def test_invalid_message_data(self):
        # Validate with missing content, should fail validation
        data = {
            'sender': self.sender.id,
            'receiver': self.receiver.id,
            'content': ''
        }
        serializer = MessageSerializer(data=data)

        # Serializer should not be valid with empty content
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)
