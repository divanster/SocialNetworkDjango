# backend/friends/tests/test_serializers.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from friends.models import FriendRequest, Friendship
from friends.serializers import FriendRequestSerializer, FriendshipSerializer
from rest_framework.exceptions import ValidationError

User = get_user_model()


class FriendRequestSerializerTests(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@example.com',
            username='sender',
            password='password1'
        )
        self.receiver = User.objects.create_user(
            email='receiver@example.com',
            username='receiver',
            password='password2'
        )

    def test_friend_request_serializer_create(self):
        data = {
            'receiver': self.receiver.id,
        }
        serializer = FriendRequestSerializer(data=data)
        serializer.context['request'] = type('Request', (object,),
                                             {'user': self.sender})()
        self.assertTrue(serializer.is_valid(), serializer.errors)
        friend_request = serializer.save(sender=self.sender)
        self.assertEqual(friend_request.sender, self.sender)
        self.assertEqual(friend_request.receiver, self.receiver)
        self.assertEqual(friend_request.status, 'pending')

    def test_friend_request_serializer_validation(self):
        data = {}
        serializer = FriendRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('receiver', serializer.errors)


class FriendshipSerializerTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password2'
        )
        self.friendship = Friendship.objects.create(user1=self.user1, user2=self.user2)

    def test_friendship_serializer(self):
        serializer = FriendshipSerializer(instance=self.friendship)
        data = serializer.data
        self.assertEqual(data['user1'], self.user1.id)
        self.assertEqual(data['user2'], self.user2.id)
