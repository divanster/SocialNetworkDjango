from rest_framework.test import APITestCase
from follows.serializers import FollowSerializer
from follows.models import Follow
from django.contrib.auth import get_user_model

User = get_user_model()


class FollowSerializerTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

    def test_follow_serialization(self):
        # Create a follow instance
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)

        # Serialize the follow instance
        serializer = FollowSerializer(follow)
        expected_data = {
            'id': follow.id,
            'follower': self.user1.id,
            'followed': self.user2.id,
            'created_at': follow.created_at.isoformat(),
        }

        self.assertEqual(serializer.data, expected_data)

    def test_follow_deserialization(self):
        # Validate input data for creating a new follow
        data = {
            'follower': self.user1.id,
            'followed': self.user2.id,
        }
        serializer = FollowSerializer(data=data)

        # Serializer should be valid with correct input data
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['follower'], self.user1)
        self.assertEqual(serializer.validated_data['followed'], self.user2)
