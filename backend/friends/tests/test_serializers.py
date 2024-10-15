from rest_framework.test import APITestCase
from friends.serializers import FriendRequestSerializer, FriendshipSerializer
from friends.models import FriendRequest, Friendship
from django.contrib.auth import get_user_model

User = get_user_model()


class FriendSerializerTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

    def test_friend_request_serialization(self):
        # Create a friend request instance
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)
        serializer = FriendRequestSerializer(friend_request)
        expected_data = {
            'id': friend_request.id,
            'sender': self.user1.id,
            'receiver': self.user2.id,
            'created_at': friend_request.created_at.isoformat(),
            'status': friend_request.status,
        }
        self.assertEqual(serializer.data, expected_data)

    def test_friendship_serialization(self):
        # Create a friendship instance
        friendship = Friendship.objects.create(user1_id=self.user1.id,
                                               user1_username=self.user1.username,
                                               user2_id=self.user2.id,
                                               user2_username=self.user2.username)
        serializer = FriendshipSerializer(friendship)
        expected_data = {
            'id': friendship.id,
            'user1': self.user1.id,
            'user2': self.user2.id,
            'created_at': friendship.created_at.isoformat(),
        }
        self.assertEqual(serializer.data, expected_data)
