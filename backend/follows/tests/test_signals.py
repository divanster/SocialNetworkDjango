from django.test import TestCase
from unittest.mock import patch
from follows.models import Follow
from django.contrib.auth import get_user_model

User = get_user_model()


class FollowSignalsTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

    @patch('follows.signals.KafkaProducerClient.send_message')
    def test_follow_created_signal(self, mock_send_message):
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)
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
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)
        follow.delete()
        mock_send_message.assert_called_once_with('FOLLOW_EVENTS', {
            "follow_id": follow.id,
            "action": "deleted"
        })
