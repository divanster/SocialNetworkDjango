from django.test import TestCase
from friends.models import FriendRequest, Friendship
from friends.tasks import send_friend_event_to_kafka
from unittest.mock import patch
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class FriendTasksTestCase(TestCase):
    """
    Test case for Celery tasks in the 'friends' app to verify correct behavior
    of Kafka messages being sent when FriendRequest or Friendship tasks are executed.
    """

    def setUp(self):
        """
        Set up initial data for testing the tasks.
        - Create two user instances: user1 and user2.
        - Create a friend request instance between user1 and user2.
        """
        # Create two test users
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

        # Create a friend request from user1 to user2
        self.friend_request = FriendRequest.objects.create(
            sender_id=self.user1.id,
            sender_username=self.user1.username,
            receiver_id=self.user2.id,
            receiver_username=self.user2.username
        )

    @patch('friends.tasks.KafkaProducerClient.send_message')
    def test_send_friend_event_to_kafka(self, mock_send_message):
        """
        Test that the Celery task `send_friend_event_to_kafka` sends the correct
        Kafka message when a friend request is created.
        """
        # Execute the task to send the friend request event to Kafka
        send_friend_event_to_kafka(self.friend_request.id, 'created', is_friendship=False)

        # Assert that the Kafka producer's `send_message()` method was called with
        # the correct arguments
        mock_send_message.assert_called_once_with('FRIEND_EVENTS', {
            "friend_request_id": self.friend_request.id,
            "sender_id": self.user1.id,
            "receiver_id": self.user2.id,
            "status": self.friend_request.status,
            "created_at": str(self.friend_request.created_at),
            "event": "created"
        })

    @patch('friends.tasks.KafkaProducerClient.send_message')
    def test_send_friendship_event_to_kafka(self, mock_send_message):
        """
        Test that the Celery task `send_friend_event_to_kafka` sends the correct
        Kafka message when a friendship is created.
        """
        # Create a friendship instance between user1 and user2
        friendship = Friendship.objects.create(
            user1_id=min(self.user1.id, self.user2.id),
            user1_username=self.user1.username,
            user2_id=max(self.user1.id, self.user2.id),
            user2_username=self.user2.username
        )

        # Execute the task to send the friendship event to Kafka
        send_friend_event_to_kafka(friendship.id, 'created', is_friendship=True)

        # Assert that the Kafka producer's `send_message()` method was called with the correct arguments
        mock_send_message.assert_called_once_with('FRIEND_EVENTS', {
            "friendship_id": friendship.id,
            "user1_id": friendship.user1_id,
            "user2_id": friendship.user2_id,
            "created_at": str(friendship.created_at),
            "event": "created"
        })

