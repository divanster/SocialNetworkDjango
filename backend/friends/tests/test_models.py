# backend/friends/tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from friends.models import FriendRequest, Friendship, Block
from django.core.exceptions import ValidationError

User = get_user_model()


class FriendRequestModelTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password2'
        )

    def test_create_friend_request(self):
        friend_request = FriendRequest.objects.create(sender=self.user1,
                                                      receiver=self.user2)
        self.assertEqual(friend_request.status, 'pending')
        self.assertEqual(str(friend_request),
                         f"{self.user1.username} -> {self.user2.username} (pending)")

    def test_unique_together_constraint(self):
        FriendRequest.objects.create(sender=self.user1, receiver=self.user2)
        with self.assertRaises(Exception):
            FriendRequest.objects.create(sender=self.user1, receiver=self.user2)

    def test_cannot_send_request_if_blocked(self):
        Block.objects.create(blocker=self.user1, blocked=self.user2)
        with self.assertRaises(ValidationError):
            friend_request = FriendRequest(sender=self.user1, receiver=self.user2)
            friend_request.clean()


class FriendshipModelTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password2'
        )

    def test_create_friendship(self):
        friendship = Friendship.objects.create(user1=self.user1, user2=self.user2)
        self.assertEqual(str(friendship),
                         f"{self.user1.username} & {self.user2.username}")

    def test_unique_friendship_constraint(self):
        Friendship.objects.create(user1=self.user1, user2=self.user2)
        with self.assertRaises(Exception):
            Friendship.objects.create(user1=self.user1, user2=self.user2)

    def test_cannot_create_friendship_if_blocked(self):
        Block.objects.create(blocker=self.user1, blocked=self.user2)
        with self.assertRaises(ValidationError):
            friendship = Friendship(user1=self.user1, user2=self.user2)
            friendship.clean()


class BlockModelTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password2'
        )

    def test_create_block(self):
        block = Block.objects.create(blocker=self.user1, blocked=self.user2)
        self.assertEqual(str(block),
                         f"{self.user1.username} blocked {self.user2.username}")

    def test_cannot_block_self(self):
        with self.assertRaises(ValidationError):
            block = Block(blocker=self.user1, blocked=self.user1)
            block.clean()

    def test_unique_block_constraint(self):
        Block.objects.create(blocker=self.user1, blocked=self.user2)
        with self.assertRaises(Exception):
            Block.objects.create(blocker=self.user1, blocked=self.user2)
