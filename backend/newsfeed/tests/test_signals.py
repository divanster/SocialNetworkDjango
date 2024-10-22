from django.test import TestCase
from unittest.mock import patch
from social.models import Post
from django.contrib.auth import get_user_model
from newsfeed.signals import handle_model_save, handle_model_delete
from django.db.models.signals import post_save, post_delete

User = get_user_model()


class TestNewsfeedSignals(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        # Connect signals for testing
        post_save.connect(handle_model_save, sender=Post)
        post_delete.connect(handle_model_delete, sender=Post)

    def tearDown(self):
        # Disconnect signals to avoid side effects on other tests
        post_save.disconnect(handle_model_save, sender=Post)
        post_delete.disconnect(handle_model_delete, sender=Post)

    @patch('newsfeed.signals.send_newsfeed_event_to_kafka.delay')
    def test_post_created_signal(self, mock_task):
        # Create a post to trigger the post_save signal
        post = Post.objects.create(author=self.user, title='Test Post', content='Test Content')

        # Verify that the task was called with correct arguments
        mock_task.assert_called_once_with(post.id, 'created', 'Post')

    @patch('newsfeed.signals.send_newsfeed_event_to_kafka.delay')
    def test_post_deleted_signal(self, mock_task):
        # Create and then delete a post to trigger the post_delete signal
        post = Post.objects.create(author=self.user, title='Test Post', content='Test Content')
        post.delete()

        # Verify that the task was called with correct arguments
        mock_task.assert_called_once_with(post.id, 'deleted', 'Post')
