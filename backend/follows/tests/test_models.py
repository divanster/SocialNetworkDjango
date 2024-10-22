from django.test import TestCase
from django.contrib.auth import get_user_model
from follows.models import Follow

# Get the custom User model
User = get_user_model()


class FollowModelTestCase(TestCase):
    """
    Test case for the Follow model.
    This includes:
    - Testing the creation of a follow relationship.
    - Verifying the __str__ method's output.
    - Testing constraints like unique follow relationships and cascading deletions.
    """

    def setUp(self):
        """
        Set up the initial state for the test cases.
        - Create two users to test the follow relationship.
        """
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

    def test_create_follow(self):
        """
        Test the creation of a follow relationship.
        - Ensure that the follow relationship is correctly created.
        - Validate the 'follower' and 'followed' fields.
        """
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)

        # Check that there is exactly one follow relationship in the database
        self.assertEqual(Follow.objects.count(), 1,
                         "Follow relationship count should be 1 after creation.")

        # Verify that the follower and followed users are set correctly
        self.assertEqual(follow.follower, self.user1, "Follower should be user1.")
        self.assertEqual(follow.followed, self.user2, "Followed should be user2.")

    def test_str_method(self):
        """
        Test the __str__ method of the Follow model.
        - Ensure that the string representation matches the expected format.
        """
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)

        # Check that the __str__ method returns the correct string
        self.assertEqual(str(follow), "user1 follows user2",
                         "__str__ output does not match the expected format.")

    def test_prevent_duplicate_follow(self):
        """
        Test that a user cannot follow the same user more than once.
        - Ensure that the unique constraint between 'follower' and 'followed' is enforced.
        """
        # Create the initial follow relationship
        Follow.objects.create(follower=self.user1, followed=self.user2)

        # Attempt to create a duplicate follow, which should raise an IntegrityError
        with self.assertRaises(Exception) as context:
            Follow.objects.create(follower=self.user1, followed=self.user2)

        # Check the raised exception is due to the unique constraint
        self.assertTrue('unique constraint' in str(context.exception).lower(),
                        "Duplicate follow should raise a unique constraint error.")

    def test_prevent_self_follow(self):
        """
        Test that a user cannot follow themselves.
        - Ensure that self-following raises a validation error or is not allowed.
        """
        with self.assertRaises(ValueError):
            Follow.objects.create(follower=self.user1, followed=self.user1)

    def test_follow_deletion_on_user_delete(self):
        """
        Test that follows are deleted when the user is deleted.
        - Ensure that the follow relationships involving the deleted user are also removed.
        """
        # Create a follow relationship
        Follow.objects.create(follower=self.user1, followed=self.user2)

        # Delete user1 and verify that the follow relationship is removed
        self.user1.delete()
        self.assertEqual(Follow.objects.count(), 0,
                         "Follow relationships should be deleted when a user is deleted.")

        # Create a follow relationship again
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        Follow.objects.create(follower=self.user1, followed=self.user2)

        # Delete user2 and verify that the follow relationship is removed
        self.user2.delete()
        self.assertEqual(Follow.objects.count(), 0,
                         "Follow relationships should be deleted when a followed user is deleted.")

    def test_follow_reciprocal_relationship(self):
        """
        Test creating reciprocal follow relationships.
        - Ensure user1 can follow user2 and vice versa without issues.
        """
        follow1 = Follow.objects.create(follower=self.user1, followed=self.user2)
        follow2 = Follow.objects.create(follower=self.user2, followed=self.user1)

        self.assertEqual(Follow.objects.count(), 2,
                         "There should be 2 reciprocal follow relationships.")
        self.assertIn(follow1, Follow.objects.all(),
                      "Follow1 relationship should exist.")
        self.assertIn(follow2, Follow.objects.all(),
                      "Follow2 relationship should exist.")

    # Tear down method for cleanup, in case it's needed for test optimization.
    def tearDown(self):
        Follow.objects.all().delete()
        User.objects.all().delete()
