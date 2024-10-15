from django.test import TestCase
from unittest.mock import patch
from friends.models import FriendRequest, Friendship
from django.contrib.auth import get_user_model

User = get_user_model()


class FriendSignalsTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

    @patch('friends.signals.KafkaProducerClient.send_message')
    def test_friend_request_created_signal(self, mock_send_message):
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)
        mock_send_message.assert_called_once_with('FRIEND_EVENTS', {
            "friend_request_id": friend_request.id,
            "sender_id": self.user1.id,
            "receiver_id": self.user2.id,
            "status": friend_request.status,
            "created_at": str(friend_request.created_at),
            "event": "created"
        })

    @patch('friends.signals.KafkaProducerClient.send_message')
    def test_friendship_created_signal(self, mock_send_message):
        friendship = Friendship.objects.create(user1_id=self.user1.id,
                                               user1_username=self.user1.username,
                                               user2_id=self.user2.id,
                                               user2_username=self.user2.username)
        mock_send_message.assert_called_once_with('FRIEND_EVENTS', {
            "friendship_id": friendship.id,
            "user1_id": self.user1.id,
            "user2_id": self.user2.id,
            "created_at": str(friendship.created_at),
            "event": "created"
        })
