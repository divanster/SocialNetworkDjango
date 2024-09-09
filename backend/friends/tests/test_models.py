from django.test import TestCase
from django.contrib.auth import get_user_model
from friends.models import FriendRequest, Friendship, Block
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

User = get_user_model()


class FriendTests(TestCase):

    def setUp(self):
        # Create test users with username, email, and password
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='password'
        )

    def test_create_friend_request(self):
        # Test creating a friend request
        friend_request = FriendRequest.objects.create(sender=self.user1,
                                                      receiver=self.user2)
        self.assertEqual(friend_request.status, 'pending')
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_accept_friend_request(self):
        # Test accepting a friend request and creating a friendship
        friend_request = FriendRequest.objects.create(sender=self.user1,
                                                      receiver=self.user2)
        friend_request.status = 'accepted'
        friend_request.save()

        # Check that the friendship is automatically created
        friendship = Friendship.objects.get(user1=self.user1, user2=self.user2)
        self.assertIsNotNone(friendship)
        self.assertEqual(Friendship.objects.count(), 1)

    def test_reject_friend_request(self):
        # Test rejecting a friend request
        friend_request = FriendRequest.objects.create(sender=self.user1,
                                                      receiver=self.user2)
        friend_request.status = 'rejected'
        friend_request.save()

        # Ensure no friendship was created
        with self.assertRaises(Friendship.DoesNotExist):
            Friendship.objects.get(user1=self.user1, user2=self.user2)

        # Ensure the friend request is marked as rejected
        self.assertEqual(friend_request.status, 'rejected')

    def test_unique_pending_friend_request(self):
        # Test unique pending friend request constraint
        FriendRequest.objects.create(sender=self.user1, receiver=self.user2)

        # Ensure that creating a duplicate friend request raises an IntegrityError
        with self.assertRaises(IntegrityError):
            FriendRequest.objects.create(sender=self.user1, receiver=self.user2)

    def test_block_user(self):
        # Test blocking a user
        block = Block.objects.create(blocker=self.user1, blocked=self.user2)
        self.assertEqual(Block.objects.count(), 1)
        self.assertTrue(
            Block.objects.filter(blocker=self.user1, blocked=self.user2).exists())

    def test_block_prevents_friend_request(self):
        # Test that blocked users cannot send friend requests
        Block.objects.create(blocker=self.user1, blocked=self.user2)
        with self.assertRaises(ValidationError):
            FriendRequest.objects.create(sender=self.user1, receiver=self.user2)

    def test_block_prevents_friendship(self):
        # Test that blocked users cannot become friends
        Block.objects.create(blocker=self.user1, blocked=self.user2)

        # Check that creating a friend request between blocked users raises a ValidationError
        with self.assertRaises(ValidationError):
            FriendRequest.objects.create(sender=self.user1, receiver=self.user2)

    def test_friendship_created_after_accepting_request(self):
        # Test that friendship is created only after the friend request is accepted
        friend_request = FriendRequest.objects.create(sender=self.user1,
                                                      receiver=self.user2)
        self.assertEqual(Friendship.objects.count(), 0)  # No friendship yet

        # Accept the friend request
        friend_request.status = 'accepted'
        friend_request.save()

        # Now friendship should be created
        self.assertEqual(Friendship.objects.count(), 1)
        self.assertTrue(
            Friendship.objects.filter(user1=self.user1, user2=self.user2).exists())

    def test_block_prevents_reverse_friendship(self):
        # Test that friendship isn't created if the receiver blocks the sender after
        # the request
        Block.objects.create(blocker=self.user2, blocked=self.user1)

        # Check that creating a friend request raises a ValidationError
        with self.assertRaises(ValidationError):
            FriendRequest.objects.create(sender=self.user1, receiver=self.user2)

    def test_str_methods(self):
        # Test the __str__ methods for FriendRequest, Friendship, and Block
        friend_request = FriendRequest.objects.create(sender=self.user1,
                                                      receiver=self.user2)
        self.assertEqual(str(friend_request),
                         f"{self.user1.username} -> {self.user2.username} (pending)")

        friend_request.status = 'accepted'
        friend_request.save()
        friendship = Friendship.objects.get(user1=self.user1, user2=self.user2)
        self.assertEqual(str(friendship),
                         f"{self.user1.username} & {self.user2.username}")

        block = Block.objects.create(blocker=self.user1, blocked=self.user2)
        self.assertEqual(str(block),
                         f"{self.user1.username} blocked {self.user2.username}")
