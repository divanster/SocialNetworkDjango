from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from friends.models import FriendRequest, Friendship
from unittest.mock import patch

# Get the custom User model
User = get_user_model()


class FriendRequestViewSetTestCase(APITestCase):
    """
    Test case for FriendRequestViewSet to verify CRUD operations for friend requests.
    """

    def setUp(self):
        """
        Set up initial data for tests:
        - Create two test users: user1 and user2.
        - Authenticate as user1 by default for all tests.
        """
        self.client = APIClient()

        # Create two users for testing friend request operations
        self.user1 = User.objects.create_user(
            email='user1@example.com', username='user1', password='password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com', username='user2', password='password123'
        )

        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

    @patch('friends.views.KafkaProducerClient.send_message')
    def test_create_friend_request(self, mock_send_message):
        """
        Test creating a friend request from user1 to user2.
        Ensure that the request is successfully created and Kafka event is sent.
        """
        url = reverse('friendrequest-list')
        data = {
            'receiver': self.user2.id  # Set the receiver to user2
        }

        # Send POST request to create a friend request
        response = self.client.post(url, data)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendRequest.objects.count(), 1)
        mock_send_message.assert_called_once()  # Verify Kafka producer was called

    @patch('friends.views.KafkaProducerClient.send_message')
    def test_accept_friend_request(self, mock_send_message):
        """
        Test accepting a friend request by the receiver (user2).
        Ensure that the status is updated to 'accepted', and a Friendship instance is created.
        """
        # Create a friend request from user1 to user2
        friend_request = FriendRequest.objects.create(
            sender_id=self.user1.id,
            sender_username=self.user1.username,
            receiver_id=self.user2.id,
            receiver_username=self.user2.username
        )

        # Authenticate as user2 (receiver)
        self.client.force_authenticate(user=self.user2)

        # URL for the friend request
        url = reverse('friendrequest-detail', kwargs={'id': friend_request.id})
        data = {'status': 'accepted'}  # Payload to accept the request

        # Send PATCH request to accept the friend request
        response = self.client.patch(url, data)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FriendRequest.objects.get(id=friend_request.id).status, 'accepted')
        self.assertEqual(Friendship.objects.count(), 1)
        mock_send_message.assert_called()  # Verify Kafka producer was called

    @patch('friends.views.KafkaProducerClient.send_message')
    def test_reject_friend_request(self, mock_send_message):
        """
        Test rejecting a friend request by the receiver (user2).
        Ensure that the status is updated to 'rejected'.
        """
        # Create a friend request from user1 to user2
        friend_request = FriendRequest.objects.create(
            sender_id=self.user1.id,
            sender_username=self.user1.username,
            receiver_id=self.user2.id,
            receiver_username=self.user2.username
        )

        # Authenticate as user2 (receiver)
        self.client.force_authenticate(user=self.user2)

        # URL for the friend request
        url = reverse('friendrequest-detail', kwargs={'id': friend_request.id})
        data = {'status': 'rejected'}  # Payload to reject the request

        # Send PATCH request to reject the friend request
        response = self.client.patch(url, data)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FriendRequest.objects.get(id=friend_request.id).status, 'rejected')
        mock_send_message.assert_called()  # Verify Kafka producer was called

    def test_accept_friend_request_invalid_user(self):
        """
        Test accepting a friend request by a user other than the intended receiver.
        This should return a 400 Bad Request error.
        """
        # Create a friend request from user1 to user2
        friend_request = FriendRequest.objects.create(
            sender_id=self.user1.id,
            sender_username=self.user1.username,
            receiver_id=self.user2.id,
            receiver_username=self.user2.username
        )

        # Authenticate as user1 (sender), who should not be allowed to accept the request
        self.client.force_authenticate(user=self.user1)

        # URL for the friend request
        url = reverse('friendrequest-detail', kwargs={'id': friend_request.id})
        data = {'status': 'accepted'}

        # Send PATCH request to accept the friend request
        response = self.client.patch(url, data)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You do not have permission to accept this request.")


