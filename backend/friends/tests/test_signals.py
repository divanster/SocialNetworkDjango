# backend/friends/tests/test_signals.py

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from friends.models import FriendRequest, Friendship, Block
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from unittest.mock import patch, MagicMock
from django.core import mail

User = get_user_model()


@override_settings(
    CHANNEL_LAYERS={
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
)
class FriendSignalsTests(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@example.com',
            username='sender',
            password='password1'
        )
        self.receiver = User.objects.create_user(
            email='receiver@example.com',
            username='receiver',
            password='password2'
        )
        self.channel_layer = get_channel_layer()
        async_to_sync(self.channel_layer.flush)()

    @patch('friends.signals.send_mail')
    def test_friend_request_created_signal(self, mock_send_mail):
        with patch('friends.signals.send_real_time_notification') as mock_notification:
            FriendRequest.objects.create(sender=self.sender, receiver=self.receiver)
            mock_notification.assert_called_with(
                self.receiver.id,
                f"You have a new friend request from {self.sender.username}.",
                'friend_request_notification'
            )
            mock_send_mail.assert_called_once()
            # Check that an email was sent
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('New Friend Request', mail.outbox[0].subject)

    def test_friend_request_accepted_signal(self):
        with patch('friends.signals.send_real_time_notification') as mock_notification:
            friend_request = FriendRequest.objects.create(sender=self.sender,
                                                          receiver=self.receiver)
            friend_request.status = 'accepted'
            friend_request.save()
            mock_notification.assert_called_with(
                self.sender.id,
                f"You are now friends with {self.receiver.username}.",
                'friendship_notification'
            )
            self.assertEqual(Friendship.objects.count(), 1)

    def test_friend_request_deleted_signal(self):
        with patch('friends.signals.send_real_time_notification') as mock_notification:
            friend_request = FriendRequest.objects.create(sender=self.sender,
                                                          receiver=self.receiver)
            friend_request.delete()
            self.assertEqual(mock_notification.call_count, 2)
            calls = [
                ((self.receiver.id,
                  f"Friend request from {self.sender.username} has been deleted.",
                  'friend_request_notification'),),
                ((self.sender.id,
                  f"Your friend request to {self.receiver.username} has been deleted.",
                  'friend_request_notification'),)
            ]
            mock_notification.assert_has_calls(calls, any_order=True)

    def test_friendship_created_signal(self):
        with patch('friends.signals.send_real_time_notification') as mock_notification:
            Friendship.objects.create(user1=self.sender, user2=self.receiver)
            self.assertEqual(mock_notification.call_count, 2)
            calls = [
                ((self.sender.id, f"You are now friends with {self.receiver.username}.",
                  'friendship_notification'),),
                ((self.receiver.id, f"You are now friends with {self.sender.username}.",
                  'friendship_notification'),)
            ]
            mock_notification.assert_has_calls(calls, any_order=True)

    def test_friendship_deleted_signal(self):
        with patch('friends.signals.send_real_time_notification') as mock_notification:
            friendship = Friendship.objects.create(user1=self.sender,
                                                   user2=self.receiver)
            friendship.delete()
            self.assertEqual(mock_notification.call_count, 2)
            calls = [
                ((self.sender.id,
                  f"Your friendship with {self.receiver.username} has been removed.",
                  'friendship_notification'),),
                ((self.receiver.id,
                  f"Your friendship with {self.sender.username} has been removed.",
                  'friendship_notification'),)
            ]
            mock_notification.assert_has_calls(calls, any_order=True)
