from django.test import TestCase
from unittest.mock import patch
from social.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()


class TestNewsfeedSignals(TestCase):
    @patch('newsfeed.signals.send_newsfeed_event_to_kafka.delay')
    def test_post_created_signal(self, mock_task):
        user = User.objects.create_user(username='testuser', email='test@example.com',
                                        password='password')
        post = Post.objects.create(author=user, title='Test Post',
                                   content='Test Content')

        # Verify that the task was called
        mock_task.assert_called_once_with(post.id, 'created', 'Post')

    @patch('newsfeed.signals.send_newsfeed_event_to_kafka.delay')
    def test_post_deleted_signal(self, mock_task):
        user = User.objects.create_user(username='testuser', email='test@example.com',
                                        password='password')
        post = Post.objects.create(author=user, title='Test Post',
                                   content='Test Content')
        post.delete()

        # Verify that the task was called
        mock_task.assert_called_with(post.id, 'deleted', 'Post')
