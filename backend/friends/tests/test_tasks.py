from django.test import TestCase
from friends.models import FriendRequest, Friendship
from friends.tasks import send_friend_event_to_kafka
from unittest.mock import patch
from django.contrib.auth import get_user_model

User = get_user_model()


class FriendTasksTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')
        self.friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                           sender_username=self.user1.username,
                                                           receiver_id=self.user2.id,
                                                           receiver_username=self.user2.username)

    @patch('friends.tasks.KafkaProducerClient.send_message')
    def test_send_friend_event_to_kafka(self, mock_send_message):
        send_friend_event_to_kafka(self.friend_request.id, 'created',
                                   is_friendship=False)
        mock_send_message.assert_called_once_with('FRIEND_EVENTS', {
            "friend_request_id": self.friend_request.id,
            "sender_id": self.user1.id,
            "receiver_id": self.user2.id,
            "status": self.friend_request.status,
            "created_at": str(self.friend_request.created_at),
            "event": "created"
        })
