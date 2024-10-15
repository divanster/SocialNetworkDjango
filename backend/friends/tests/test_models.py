from django.test import TestCase
from django.core.exceptions import ValidationError
from friends.models import FriendRequest, Friendship, Block
from django.contrib.auth import get_user_model

User = get_user_model()


class FriendModelsTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')
        self.user3 = User.objects.create_user(email='user3@example.com',
                                              username='user3', password='password123')

    def test_create_friend_request(self):
        # Test creation of a friend request
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)
        self.assertEqual(FriendRequest.objects.count(), 1)
        self.assertEqual(friend_request.status, 'pending')

    def test_reject_friend_request(self):
        # Test rejecting a friend request
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)
        friend_request.status = 'rejected'
        friend_request.save()
        self.assertEqual(friend_request.status, 'rejected')

    def test_unique_friend_request(self):
        # Test that duplicate friend requests cannot be created
        FriendRequest.objects.create(sender_id=self.user1.id,
                                     sender_username=self.user1.username,
                                     receiver_id=self.user2.id,
                                     receiver_username=self.user2.username)
        with self.assertRaises(ValidationError):
            duplicate_request = FriendRequest(sender_id=self.user1.id,
                                              sender_username=self.user1.username,
                                              receiver_id=self.user2.id,
                                              receiver_username=self.user2.username)
            duplicate_request.full_clean()

    def test_create_friendship(self):
        # Test creation of a friendship
        friendship = Friendship.objects.create(
            user1_id=min(self.user1.id, self.user2.id),
            user1_username=self.user1.username,
            user2_id=max(self.user1.id, self.user2.id),
            user2_username=self.user2.username)
        self.assertEqual(Friendship.objects.count(), 1)
        self.assertEqual(friendship.user1_username, 'user1')
        self.assertEqual(friendship.user2_username, 'user2')

    def test_block_user(self):
        # Test creation of a block
        block = Block.objects.create(blocker_id=self.user1.id,
                                     blocker_username=self.user1.username,
                                     blocked_id=self.user3.id,
                                     blocked_username=self.user3.username)
        self.assertEqual(Block.objects.count(), 1)
        self.assertEqual(block.blocker_username, 'user1')

    def test_unblock_user(self):
        # Test removing a block
        block = Block.objects.create(blocker_id=self.user1.id,
                                     blocker_username=self.user1.username,
                                     blocked_id=self.user3.id,
                                     blocked_username=self.user3.username)
        block.delete()
        self.assertEqual(Block.objects.count(), 0)
