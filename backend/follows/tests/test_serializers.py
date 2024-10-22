from rest_framework.test import APITestCase
from follows.serializers import FollowSerializer
from follows.models import Follow
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Get the custom User model
User = get_user_model()

class FollowSerializerTestCase(APITestCase):
    """
    Test case for the FollowSerializer.
    This includes:
    - Testing serialization of a Follow instance.
    - Testing deserialization and validation logic.
    """

    def setUp(self):
        """
        Set up initial state for the test cases.
        - Create two users to test follow relationships.
        """
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

    def test_follow_serialization(self):
        """
        Test serialization of a follow relationship.
        - Create a follow relationship and serialize it.
        - Ensure that the serialized data matches the follow instance.
        """
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

        # Check that serialized data matches the expected data
        self.assertEqual(serializer.data, expected_data, "Serialized data does not match the follow instance.")

    def test_follow_deserialization(self):
        """
        Test deserialization of a follow relationship.
        - Ensure that input data is correctly deserialized to create a new Follow instance.
        """
        # Validate input data for creating a new follow
        data = {
            'follower': self.user1.id,
            'followed': self.user2.id,
        }
        serializer = FollowSerializer(data=data)

        # Serializer should be valid with correct input data
        self.assertTrue(serializer.is_valid(), "Serializer should be valid with correct input data.")
        validated_data = serializer.validated_data

        # Check the deserialized data
        self.assertEqual(validated_data['follower'], self.user1, "Follower does not match the expected user.")
        self.assertEqual(validated_data['followed'], self.user2, "Followed does not match the expected user.")

    def test_duplicate_follow_validation(self):
        """
        Test that creating a duplicate follow relationship raises a validation error.
        - Ensure that the unique constraint between 'follower' and 'followed' is enforced.
        """
        # Create an initial follow relationship
        Follow.objects.create(follower=self.user1, followed=self.user2)

        # Attempt to create a duplicate follow
        data = {
            'follower': self.user1.id,
            'followed': self.user2.id,
        }
        serializer = FollowSerializer(data=data)

        # Serializer should not be valid with duplicate data
        self.assertFalse(serializer.is_valid(), "Serializer should be invalid for duplicate follow relationships.")
        self.assertIn('non_field_errors', serializer.errors, "Expected validation error for duplicate follow.")

    def test_self_follow_validation(self):
        """
        Test that a user cannot follow themselves.
        - Ensure that self-following raises a validation error.
        """
        # Attempt to create a follow relationship where the follower is the same as the followed user
        data = {
            'follower': self.user1.id,
            'followed': self.user1.id,
        }
        serializer = FollowSerializer(data=data)

        # Serializer should be invalid for self-following
        self.assertFalse(serializer.is_valid(), "Serializer should be invalid for self-follow relationships.")
        self.assertIn('non_field_errors', serializer.errors, "Expected validation error for self-follow relationships.")

    def test_create_follow(self):
        """
        Test the successful creation of a follow relationship.
        - Ensure that the follow relationship is saved correctly to the database.
        """
        data = {
            'follower': self.user1.id,
            'followed': self.user2.id,
        }
        serializer = FollowSerializer(data=data)

        # Ensure the serializer is valid and save the follow instance
        self.assertTrue(serializer.is_valid(), "Serializer should be valid with correct input data.")
        follow = serializer.save()

        # Validate that the follow instance was correctly saved
        self.assertEqual(Follow.objects.count(), 1, "There should be one follow relationship in the database.")
        self.assertEqual(follow.follower, self.user1, "Follower does not match the expected user.")
        self.assertEqual(follow.followed, self.user2, "Followed does not match the expected user.")


    def tearDown(self):
        """
        Tear down the test setup after each test case runs.
        - Delete all follow relationships and user instances.
        """
        Follow.objects.all().delete()
        User.objects.all().delete()
