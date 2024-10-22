from rest_framework.test import APITestCase
from friends.serializers import FriendRequestSerializer, FriendshipSerializer
from friends.models import FriendRequest, Friendship
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class FriendSerializerTestCase(APITestCase):
    """
    Test case for FriendRequestSerializer and FriendshipSerializer to validate
    the correct serialization of FriendRequest and Friendship model instances.
    """

    def setUp(self):
        """
        Set up users for the tests.
        """
        # Create two users to use for friend request and friendship
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

    def test_friend_request_serialization(self):
        """
        Test the serialization of a FriendRequest instance.
        """
        # Create a friend request from user1 to user2
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)

        # Serialize the friend request instance
        serializer = FriendRequestSerializer(friend_request)
        expected_data = {
            'id': friend_request.id,  # Ensure the correct id is serialized
            'sender': self.user1.id,  # Verify the sender's ID
            'receiver': self.user2.id,  # Verify the receiver's ID
            'created_at': friend_request.created_at.isoformat(),  # Check the timestamp format
            'status': friend_request.status,  # Ensure the status field is serialized properly
        }

        # Validate that serialized data matches the expected data
        self.assertEqual(serializer.data, expected_data)

    def test_friendship_serialization(self):
        """
        Test the serialization of a Friendship instance.
        """
        # Create a friendship between user1 and user2
        friendship = Friendship.objects.create(user1_id=self.user1.id,
                                               user1_username=self.user1.username,
                                               user2_id=self.user2.id,
                                               user2_username=self.user2.username)

        # Serialize the friendship instance
        serializer = FriendshipSerializer(friendship)
        expected_data = {
            'id': friendship.id,  # Check the serialized friendship ID
            'user1': self.user1.id,  # Verify user1's ID in the serialized output
            'user2': self.user2.id,  # Verify user2's ID in the serialized output
            'created_at': friendship.created_at.isoformat(),  # Ensure the created timestamp is serialized correctly
        }

        # Validate that serialized data matches the expected data
        self.assertEqual(serializer.data, expected_data)

