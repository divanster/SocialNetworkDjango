# tests/test_serializers.py

from django.test import TestCase
from friends.models import FriendRequest, Friendship
from friends.serializers import FriendRequestSerializer, FriendshipSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class FriendRequestSerializerTest(TestCase):

    def setUp(self):
        # Create two users for testing
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

    def test_friend_request_serialization(self):
        # Create a friend request
        friend_request = FriendRequest.objects.create(sender=self.user1,
                                                      receiver=self.user2)
        serializer = FriendRequestSerializer(friend_request)

        # Check the serialized data
        expected_data = {
            'id': friend_request.id,
            'sender': self.user1.id,
            'receiver': self.user2.id,
            'created_at': friend_request.created_at.isoformat(),
            'status': 'pending'
        }
        self.assertEqual(serializer.data, expected_data)

    def test_friend_request_deserialization(self):
        # Simulate incoming data
        data = {
            'receiver': self.user2.id
        }
        serializer = FriendRequestSerializer(data=data)

        # Validate and check if it is valid
        self.assertTrue(serializer.is_valid())
        friend_request = serializer.save(sender=self.user1)

        # Ensure the friend request was created correctly
        self.assertEqual(friend_request.sender, self.user1)
        self.assertEqual(friend_request.receiver, self.user2)
        self.assertEqual(friend_request.status, 'pending')


class FriendshipSerializerTest(TestCase):

    def setUp(self):
        # Create two users for testing
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

    def test_friendship_serialization(self):
        # Create a friendship
        friendship = Friendship.objects.create(user1=self.user1, user2=self.user2)
        serializer = FriendshipSerializer(friendship)

        # Check the serialized data
        expected_data = {
            'id': friendship.id,
            'user1': self.user1.id,
            'user2': self.user2.id,
            'created_at': friendship.created_at.isoformat(),
        }
        self.assertEqual(serializer.data, expected_data)
