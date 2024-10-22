from django.test import TestCase
from unittest.mock import patch
from follows.models import Follow
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class FollowSignalsTestCase(TestCase):
    """
    Test case for testing the signals in the Follow model.
    This includes:
    - Testing that creating a Follow instance triggers a Kafka event for follow creation.
    - Testing that deleting a Follow instance triggers a Kafka event for follow deletion.
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

    @patch('follows.signals.KafkaProducerClient.send_message')
    def test_follow_created_signal(self, mock_send_message):
        """
        Test the follow_created signal.
        - Ensure that creating a Follow instance triggers the correct Kafka event.
        - Verify that the signal sends the appropriate Kafka message for a 'created' event.
        """
        # Create a follow relationship
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)

        # Verify that the Kafka producer sends a message once, with the expected payload
        mock_send_message.assert_called_once_with('FOLLOW_EVENTS', {
            "follow_id": follow.id,
            "follower_id": follow.follower.id,
            "follower_username": follow.follower.username,
            "followed_id": follow.followed.id,
            "followed_username": follow.followed.username,
            "created_at": str(follow.created_at),
            "event": "created"
        })

    @patch('follows.signals.KafkaProducerClient.send_message')
    def test_follow_deleted_signal(self, mock_send_message):
        """
        Test the follow_deleted signal.
        - Ensure that deleting a Follow instance triggers the correct Kafka event.
        - Verify that the signal sends the appropriate Kafka message for a 'deleted' event.
        """
        # Create a follow relationship, then delete it
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)
        follow.delete()

        # Verify that the Kafka producer sends a message once, with the expected payload
        mock_send_message.assert_called_once_with('FOLLOW_EVENTS', {
            "follow_id": follow.id,
            "action": "deleted"
        })

    def tearDown(self):
        """
        Tear down the test setup after each test case runs.
        - Delete all follow relationships and user instances to ensure a clean state for every test.
        """
        Follow.objects.all().delete()
        User.objects.all().delete()
