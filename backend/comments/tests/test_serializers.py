# backend/comments/tests/test_serializers.py
from rest_framework import serializers
from rest_framework.test import APITestCase
from comments.serializers import CommentSerializer
from social.models import Post
from django.contrib.auth import get_user_model
from comments.models import Comment

User = get_user_model()


class CommentSerializerTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com',
                                             username='testuser',
                                             password='password123')
        self.post = Post.objects.create(author=self.user, title='Test Post',
                                        content='Test Post Content')

    def test_comment_serialization(self):
        # Create a comment instance
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content='Test Comment Content')

        # Serialize the comment instance
        serializer = CommentSerializer(comment)
        expected_data = {
            'id': str(comment.id),
            'user': self.user.id,
            'post': self.post.id,
            'content': 'Test Comment Content',
            'created_at': serializers.DateTimeField().to_representation(
                comment.created_at),
            'updated_at': serializers.DateTimeField().to_representation(
                comment.updated_at)
        }

        self.assertEqual(serializer.data, expected_data)

    def test_comment_deserialization(self):
        # Validate input data for creating a new comment
        data = {
            'user': self.user.id,
            'post': self.post.id,
            'content': 'New comment content'
        }
        serializer = CommentSerializer(data=data)

        # Serializer should be valid with correct input data
        self.assertTrue(serializer.is_valid())

        # Validate content field
        self.assertEqual(serializer.validated_data['content'], 'New comment content')

    def test_invalid_comment_data(self):
        # Validate with empty content, should fail validation
        data = {
            'user': self.user.id,
            'post': self.post.id,
            'content': ''
        }
        serializer = CommentSerializer(data=data)

        # Serializer should not be valid with incorrect input data
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)
