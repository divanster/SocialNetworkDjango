from django.test import TestCase
from follows.models import Follow
from follows.tasks import send_follow_event_to_kafka
from unittest.mock import patch
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class FollowTasksTestCase(TestCase):
    """
    Test case for testing Celery tasks related to Follow events.
    This includes:
    - Testing the task that sends follow events to Kafka.
    """

    def setUp(self):
        """
        Set up the initial state for tests.
        - Create two users to test follow relationships.
        - Create a Follow instance between the users.
        """
        # Creating two user instances
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

        # Creating a follow relationship between user1 and user2
        self.follow = Follow.objects.create(follower=self.user1, followed=self.user2)

    @patch('follows.tasks.KafkaProducerClient.send_message')
    def test_send_follow_event_to_kafka(self, mock_send_message):
        """
        Test that the send_follow_event_to_kafka Celery task triggers a Kafka message.
        - Ensure that creating a follow triggers the correct Kafka event.
        - Verify that the Kafka producer sends the correct message payload.
        """
        # Trigger the Celery task for a 'created' follow event
        send_follow_event_to_kafka(self.follow.id, 'created')

        # Verify that the Kafka producer sends a message once, with the expected payload
        mock_send_message.assert_called_once_with('FOLLOW_EVENTS', {
            "follow_id": self.follow.id,
            "follower_id": self.user1.id,
            "follower_username": self.user1.username,
            "followed_id": self.user2.id,
            "followed_username": self.user2.username,
            "created_at": str(self.follow.created_at),
            "event": "created"
        })

    def tearDown(self):
        """
        Tear down the test setup after each test case runs.
        - Delete all follow relationships and user instances to ensure a clean state for every test.
        """
        Follow.objects.all().delete()
        User.objects.all().delete()

