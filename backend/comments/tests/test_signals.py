from django.test import TestCase
from unittest.mock import patch
from comments.models import Comment
from social.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentSignalsTestCase(TestCase):
    """
    Test case for verifying that signals are correctly triggered when a Comment is created, updated, or deleted.
    This includes sending events to Kafka to handle comment actions.
    """

    def setUp(self):
        """
        Set up the initial data for the tests:
        - Create a user and a post to associate comments with.
        """
        # Creating a test user
        self.user = User.objects.create_user(email='user@example.com',
                                             username='testuser',
                                             password='password123')

        # Creating a test post
        self.post = Post.objects.create(author=self.user, title='Test Post',
                                        content='Some content')

    @patch('comments.signals.send_comment_event_to_kafka.delay')
    def test_comment_created_signal(self, mock_send_comment_event_to_kafka):
        """
        Test that creating a comment triggers the signal to send a Kafka event.
        - Ensure that the correct signal is fired upon comment creation.
        """
        # Create a comment, which should trigger the post_save signal
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content="Test Comment")

        # Verify that the send_comment_event_to_kafka task is called with correct
        # arguments
        mock_send_comment_event_to_kafka.assert_called_once_with(comment.comment_id, 'created')

    @patch('comments.signals.send_comment_event_to_kafka.delay')
    def test_comment_updated_signal(self, mock_send_comment_event_to_kafka):
        """
        Test that updating a comment triggers the signal to send a Kafka event.
        - Ensure that the correct signal is fired upon comment update.
        """
        # Create a comment
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content="Initial Comment")

        # Reset mock for a clean state
        mock_send_comment_event_to_kafka.reset_mock()

        # Update the comment
        comment.content = "Updated Comment"
        comment.save()

        # Verify that the send_comment_event_to_kafka task is called again with 'updated'
        mock_send_comment_event_to_kafka.assert_called_once_with(comment.comment_id, 'updated')

    @patch('comments.signals.send_comment_event_to_kafka.delay')
    def test_comment_deleted_signal(self, mock_send_comment_event_to_kafka):
        """
        Test that deleting a comment triggers the signal to send a Kafka event.
        - Ensure that the correct signal is fired upon comment deletion.
        """
        # Create a comment
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content="Test Comment")

        # Delete the comment, which should trigger the post_delete signal
        comment_id = comment.comment_id
        comment.delete()

        # Verify that the send_comment_event_to_kafka task is called with correct arguments
        mock_send_comment_event_to_kafka.assert_called_once_with(comment_id, 'deleted')

    def tearDown(self):
        """
        Clean up after each test:
        - Delete all comments, posts, and users.
        """
        Comment.objects.all().delete()
        Post.objects.all().delete()
        User.objects.all().delete()
