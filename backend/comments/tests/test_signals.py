# backend/comments/tests/test_signals.py
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

    @patch('comments.signals.KafkaProducerClient.send_message')
    def test_comment_created_signal(self, mock_send_message):
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content="Test Comment")
        mock_send_message.assert_called_once_with('COMMENT_EVENTS', {
            "comment_id": comment.id,
            "content": comment.content,
            "user_id": comment.user_id,
            "post_id": comment.post_id,
            "created_at": str(comment.created_at),
        })

    @patch('comments.signals.KafkaProducerClient.send_message')
    def test_comment_deleted_signal(self, mock_send_message):
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content="Test Comment")
        comment.delete()
        mock_send_message.assert_called_once_with('COMMENT_EVENTS', {
            "comment_id": comment.id,
            "action": "deleted"
        })
