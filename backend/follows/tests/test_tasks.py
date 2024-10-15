from django.test import TestCase
from follows.models import Follow
from follows.tasks import send_follow_event_to_kafka
from unittest.mock import patch
from django.contrib.auth import get_user_model

User = get_user_model()


class FollowTasksTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')
        self.follow = Follow.objects.create(follower=self.user1, followed=self.user2)

    @patch('follows.tasks.KafkaProducerClient.send_message')
    def test_send_follow_event_to_kafka(self, mock_send_message):
        send_follow_event_to_kafka(self.follow.id, 'created')
        mock_send_message.assert_called_once_with('FOLLOW_EVENTS', {
            "follow_id": self.follow.id,
            "follower_id": self.user1.id,
            "follower_username": self.user1.username,
            "followed_id": self.user2.id,
            "followed_username": self.user2.username,
            "created_at": str(self.follow.created_at),
            "event": "created"
        })
