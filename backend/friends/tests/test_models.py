from django.test import TestCase
from django.core.exceptions import ValidationError
from friends.models import FriendRequest, Friendship, Block
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class FriendModelsTestCase(TestCase):
    """
    Test case for testing FriendRequest, Friendship, and Block models.
    Covers creation, validation, uniqueness checks, and deletion scenarios.
    """

    def setUp(self):
        """
        Set up initial users for the tests.
        """
        # Create test users for testing friend requests, friendships, and blocks
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')
        self.user3 = User.objects.create_user(email='user3@example.com',
                                              username='user3', password='password123')

    def test_create_friend_request(self):
        """
        Test the creation of a new friend request.
        """
        # Create a friend request from user1 to user2
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)
        # Verify that one friend request has been created
        self.assertEqual(FriendRequest.objects.count(), 1)
        # Ensure the status of the friend request is 'pending' by default
        self.assertEqual(friend_request.status, 'pending')

    def test_reject_friend_request(self):
        """
        Test changing the status of a friend request to rejected.
        """
        # Create an initial friend request
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)
        # Update the friend request status to 'rejected'
        friend_request.status = 'rejected'
        friend_request.save()

        # Verify the status change
        self.assertEqual(friend_request.status, 'rejected')

    def test_unique_friend_request(self):
        """
        Test that duplicate friend requests between the same users cannot be created.
        """
        # Create an initial friend request
        FriendRequest.objects.create(sender_id=self.user1.id,
                                     sender_username=self.user1.username,
                                     receiver_id=self.user2.id,
                                     receiver_username=self.user2.username)

        # Attempt to create a duplicate friend request between the same users
        with self.assertRaises(ValidationError):
            duplicate_request = FriendRequest(sender_id=self.user1.id,
                                              sender_username=self.user1.username,
                                              receiver_id=self.user2.id,
                                              receiver_username=self.user2.username)
            # Call `full_clean` to trigger model validations, including unique constraints
            duplicate_request.full_clean()

    def test_create_friendship(self):
        """
        Test the creation of a new friendship between users.
        """
        # Create a friendship between user1 and user2
        friendship = Friendship.objects.create(
            user1_id=min(self.user1.id, self.user2.id),
            user1_username=self.user1.username,
            user2_id=max(self.user1.id, self.user2.id),
            user2_username=self.user2.username)

        # Verify that one friendship has been created
        self.assertEqual(Friendship.objects.count(), 1)
        # Validate the correct user names are associated with the friendship
        self.assertEqual(friendship.user1_username, 'user1')
        self.assertEqual(friendship.user2_username, 'user2')

    def test_block_user(self):
        """
        Test the creation of a block between two users.
        """
        # Create a block from user1 to user3
        block = Block.objects.create(blocker_id=self.user1.id,
                                     blocker_username=self.user1.username,
                                     blocked_id=self.user3.id,
                                     blocked_username=self.user3.username)

        # Verify that one block has been created
        self.assertEqual(Block.objects.count(), 1)
        # Ensure the block has the correct blocker username
        self.assertEqual(block.blocker_username, 'user1')

    def test_unblock_user(self):
        """
        Test the removal of an existing block.
        """
        # Create a block from user1 to user3
        block = Block.objects.create(blocker_id=self.user1.id,
                                     blocker_username=self.user1.username,
                                     blocked_id=self.user3.id,
                                     blocked_username=self.user3.username)

        # Delete the block to "unblock" user3
        block.delete()

        # Verify that there are no blocks remaining
        self.assertEqual(Block.objects.count(), 0)

    def test_self_block_not_allowed(self):
        """
        Test that a user cannot block themselves.
        """
        # Attempt to create a block where the blocker and blocked are the same
        with self.assertRaises(ValidationError):
            block = Block(blocker_id=self.user1.id, blocker_username=self.user1.username,
                          blocked_id=self.user1.id, blocked_username=self.user1.username)
            # Validate the model constraints, including self-block prevention
            block.full_clean()

    def test_unique_friendship_creation(self):
        """
        Test that a friendship between the same pair of users cannot be created twice.
        """
        # Create an initial friendship between user1 and user2
        Friendship.objects.create(
            user1_id=min(self.user1.id, self.user2.id),
            user1_username=self.user1.username,
            user2_id=max(self.user1.id, self.user2.id),
            user2_username=self.user2.username)

        # Attempt to create a duplicate friendship
        with self.assertRaises(ValidationError):
            duplicate_friendship = Friendship(
                user1_id=min(self.user1.id, self.user2.id),
                user1_username=self.user1.username,
                user2_id=max(self.user1.id, self.user2.id),
                user2_username=self.user2.username)
            # Trigger unique constraint validation
            duplicate_friendship.full_clean()
