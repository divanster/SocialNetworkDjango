from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from follows.models import Follow
from unittest.mock import patch

# Get the custom User model
User = get_user_model()


class FollowViewSetTestCase(APITestCase):
    """
    Test case for CRUD operations related to FollowViewSet.
    This includes creating a follow, deleting a follow, and ensuring that the
    Kafka messages are triggered properly using mocked Kafka producer.
    """

    def setUp(self):
        """
        Set up the initial state for tests.
        - Create two users to test follow relationships.
        - Authenticate the client with the created user to simulate logged-in behavior.
        """
        # Initializing API client
        self.client = APIClient()

        # Creating two user instances
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

        # Force authentication for user1 to perform follow/unfollow actions
        self.client.force_authenticate(user=self.user1)

    @patch('follows.views.KafkaProducerClient.send_message')
    def test_create_follow(self, mock_send_message):
        """
        Test creating a follow relationship between two users.
        - Ensure that the follow relationship is successfully created.
        - Validate that the Kafka producer is called to send the correct follow event.
        """
        # API endpoint to create a follow
        url = reverse('follow-list')

        # Payload to create a follow relationship
        data = {
            'followed': self.user2.id
        }

        # Send POST request to create the follow relationship
        response = self.client.post(url, data)

        # Assert that the response status code is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that the follow relationship has been created in the database
        self.assertEqual(Follow.objects.count(), 1)
        follow = Follow.objects.first()
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.followed, self.user2)

        # Verify that the Kafka producer has been called to send a message
        mock_send_message.assert_called_once()
        mock_send_message.assert_called_with('FOLLOW_EVENTS', {
            "follow_id": follow.id,
            "follower_id": follow.follower.id,
            "follower_username": follow.follower.username,
            "followed_id": follow.followed.id,
            "followed_username": follow.followed.username,
            "created_at": str(follow.created_at),
            "event": "created"
        })

    @patch('follows.views.KafkaProducerClient.send_message')
    def test_delete_follow(self, mock_send_message):
        """
        Test deleting an existing follow relationship.
        - Ensure that the follow relationship is removed from the database.
        - Validate that the Kafka producer is called to send the correct deletion event.
        """
        # Create a follow relationship to delete later
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)

        # Generate the URL to delete the specific follow instance
        url = reverse('follow-detail', kwargs={'pk': follow.pk})

        # Send DELETE request to remove the follow relationship
        response = self.client.delete(url)

        # Assert that the response status code is 204 NO CONTENT
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the follow relationship has been deleted in the database
        self.assertEqual(Follow.objects.count(), 0)

        # Verify that the Kafka producer has been called to send a deletion message
        mock_send_message.assert_called_once()
        mock_send_message.assert_called_with('FOLLOW_EVENTS', {
            "follow_id": follow.id,
            "follower_id": follow.follower.id,
            "followed_id": follow.followed.id,
            "action": "deleted"
        })

    def tearDown(self):
        """
        Tear down the test setup after each test case runs.
        - Delete all follow relationships and user instances to ensure a clean state for every test.
        """
        Follow.objects.all().delete()
        User.objects.all().delete()
