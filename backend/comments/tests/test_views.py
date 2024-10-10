# backend/comments/tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from social.models import Post
from comments.models import Comment
from comments.serializers import CommentSerializer

User = get_user_model()


class CommentViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com',
                                             username='testuser',
                                             password='password123')
        self.post = Post.objects.create(author=self.user, title='Test Post',
                                        content='Some content')
        self.client.force_authenticate(user=self.user)
        self.comment_data = {
            "post": self.post.id,
            "content": "This is a test comment",
        }

    @patch('comments.views.KafkaProducerClient.send_message')
    def test_create_comment(self, mock_send_message):
        response = self.client.post(reverse('comment-list'), self.comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        mock_send_message.assert_called_once()

    @patch('comments.views.KafkaProducerClient.send_message')
    def test_delete_comment(self, mock_send_message):
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content='Test Comment')
        response = self.client.delete(reverse('comment-detail', args=[comment.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)
        mock_send_message.assert_called_once()
