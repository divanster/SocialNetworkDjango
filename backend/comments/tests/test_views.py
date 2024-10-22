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
    """
    Test case for testing CommentViewSet CRUD operations.
    This includes creating and deleting comments while ensuring Kafka events are sent.
    """

    def setUp(self):
        """
        Set up the initial data for the tests:
        - Create a test user and authenticate the client.
        - Create a post to associate comments with.
        """
        # Create a user and post for use in the test
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='password123'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Some content'
        )
        # Authenticate the API client
        self.client.force_authenticate(user=self.user)

        # Data for creating a comment
        self.comment_data = {
            "post": str(self.post.id),  # Ensure it's a string for UUID compatibility
            "content": "This is a test comment",
            "tagged_user_ids": []
        }

    @patch('comments.views.KafkaProducerClient.send_message')
    def test_create_comment(self, mock_send_message):
        """
        Test creating a new comment.
        - Ensure that a comment is created successfully.
        - Verify that the Kafka producer's send_message method is called.
        """
        # Send a POST request to create a comment
        response = self.client.post(reverse('comment-list'), self.comment_data)

        # Assert that the response status is HTTP 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that exactly one comment has been created in the database
        self.assertEqual(Comment.objects.count(), 1)

        # Check if the created comment has the correct content
        created_comment = Comment.objects.first()
        self.assertEqual(created_comment.content, self.comment_data['content'])

        # Assert that Kafka producer send_message method was called
        mock_send_message.assert_called_once()

    @patch('comments.views.KafkaProducerClient.send_message')
    def test_delete_comment(self, mock_send_message):
        """
        Test deleting an existing comment.
        - Ensure that the comment is deleted successfully.
        - Verify that the Kafka producer's send_message method is called.
        """
        # Create a comment to be deleted later
        comment = Comment.objects.create(
            user=self.user,
            post=self.post,
            content='Test Comment'
        )

        # Send a DELETE request to delete the comment
        response = self.client.delete(reverse('comment-detail', args=[str(comment.id)]))

        # Assert that the response status is HTTP 204 NO CONTENT
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that no comments exist in the database after deletion
        self.assertEqual(Comment.objects.count(), 0)

        # Assert that Kafka producer send_message method was called
        mock_send_message.assert_called_once()

    def tearDown(self):
        """
        Clean up after each test:
        - Delete all comments, posts, and users to ensure isolated tests.
        """
        Comment.objects.all().delete()
        Post.objects.all().delete()
        User.objects.all().delete()
