# backend/comments/tests/test_serializers.py

from rest_framework import serializers
from rest_framework.test import APITestCase
from comments.serializers import CommentSerializer
from social.models import Post
from django.contrib.auth import get_user_model
from comments.models import Comment
from tagging.models import TaggedItem  # Assuming you have a tagging model for tags

User = get_user_model()

class CommentSerializerTestCase(APITestCase):
    """
    Test case for validating CommentSerializer behavior.
    This includes both serialization and deserialization of the Comment model,
    as well as validation of input data.
    """

    def setUp(self):
        """
        Set up the initial data for tests:
        - Create a user and a post to associate comments with.
        """
        # Creating a test user
        self.user = User.objects.create_user(email='user@example.com',
                                             username='testuser',
                                             password='password123')
        # Creating a test post associated with the user
        self.post = Post.objects.create(author=self.user, title='Test Post',
                                        content='Test Post Content')

    def test_comment_serialization(self):
        """
        Test the serialization of a Comment instance.
        - Ensure that the serialized data matches the Comment object properties.
        """
        # Creating a comment instance
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content='Test Comment Content')

        # Serializing the comment instance
        serializer = CommentSerializer(comment)
        expected_data = {
            'id': str(comment.comment_id),  # Ensure the comment_id is a string
            'user': self.user.id,
            'post': str(self.post.pk),  # Ensure post ID matches expected format
            'content': 'Test Comment Content',
            'created_at': serializers.DateTimeField().to_representation(
                comment.created_at),
            'updated_at': serializers.DateTimeField().to_representation(
                comment.updated_at),
            'tags': [],
            'tagged_user_ids': []
        }

        # Verifying the serialized data matches the expected data
        self.assertEqual(serializer.data, expected_data)

    def test_comment_deserialization(self):
        """
        Test the deserialization of valid input data to create a new Comment instance.
        - Ensure that valid data passes validation and is correctly deserialized.
        """
        # Valid input data for creating a comment
        data = {
            'user': self.user.id,
            'post': str(self.post.pk),
            'content': 'New comment content',
            'tagged_user_ids': []
        }
        serializer = CommentSerializer(data=data)

        # The serializer should be valid with correct input data
        self.assertTrue(serializer.is_valid())

        # Validating the content field in the deserialized data
        self.assertEqual(serializer.validated_data['content'], 'New comment content')

    def test_invalid_comment_data(self):
        """
        Test deserialization of invalid input data.
        - Ensure that missing or invalid fields fail validation.
        """
        # Invalid input data with empty content
        data = {
            'user': self.user.id,
            'post': str(self.post.pk),
            'content': ''
        }
        serializer = CommentSerializer(data=data)

        # The serializer should be invalid with incorrect input data
        self.assertFalse(serializer.is_valid())
        # Validation should include an error for the 'content' field
        self.assertIn('content', serializer.errors)

    def test_comment_serialization_with_tags(self):
        """
        Test serialization of a Comment instance with tags.
        - Ensure that tagged users are serialized properly in the output.
        """
        # Creating a comment with tagged users
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content='Comment with tags')
        tagged_user = User.objects.create_user(email='taggeduser@example.com',
                                               username='taggeduser',
                                               password='password123')
        TaggedItem.objects.create(
            content_object=comment,
            tagged_user=tagged_user,
            tagged_by=self.user
        )

        # Serializing the comment instance with tags
        serializer = CommentSerializer(comment)
        serialized_data = serializer.data

        # Verifying the tag data in the serialized output
        self.assertEqual(len(serialized_data['tags']), 1)
        self.assertEqual(serialized_data['tags'][0]['tagged_user'], tagged_user.id)

    def tearDown(self):
        """
        Clean up after each test.
        - Delete all comments, posts, users, and tags.
        """
        Comment.objects.all().delete()
        Post.objects.all().delete()
        User.objects.all().delete()
        TaggedItem.objects.all().delete()
