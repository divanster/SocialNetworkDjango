from django.test import TestCase
from unittest.mock import patch
from comments.models import Comment
from social.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentSignalsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com',
                                             username='testuser',
                                             password='password123')
        self.post = Post.objects.create(author=self.user, title='Test Post',
                                        content='Some content')

    @patch('comments.signals.send_comment_event_to_kafka.delay')
    def test_comment_created_signal(self, mock_send_comment_event_to_kafka):
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content="Test Comment")
        mock_send_comment_event_to_kafka.assert_called_once_with(comment.id, 'created')

    @patch('comments.signals.send_comment_event_to_kafka.delay')
    def test_comment_deleted_signal(self, mock_send_comment_event_to_kafka):
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content="Test Comment")
        comment.delete()
        mock_send_comment_event_to_kafka.assert_called_once_with(comment.id, 'deleted')
