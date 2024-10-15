from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from friends.models import FriendRequest, Friendship
from unittest.mock import patch

User = get_user_model()


class FriendRequestViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')
        self.client.force_authenticate(user=self.user1)

    @patch('friends.views.KafkaProducerClient.send_message')
    def test_create_friend_request(self, mock_send_message):
        url = reverse('friendrequest-list')
        data = {
            'receiver': self.user2.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendRequest.objects.count(), 1)
        mock_send_message.assert_called_once()

    @patch('friends.views.KafkaProducerClient.send_message')
    def test_accept_friend_request(self, mock_send_message):
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)
        self.client.force_authenticate(user=self.user2)
        url = reverse('friendrequest-detail', kwargs={'id': friend_request.id})
        data = {'status': 'accepted'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FriendRequest.objects.get(id=friend_request.id).status,
                         'accepted')
        self.assertEqual(Friendship.objects.count(), 1)
        mock_send_message.assert_called()

    @patch('friends.views.KafkaProducerClient.send_message')
    def test_reject_friend_request(self, mock_send_message):
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)
        self.client.force_authenticate(user=self.user2)
        url = reverse('friendrequest-detail', kwargs={'id': friend_request.id})
        data = {'status': 'rejected'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FriendRequest.objects.get(id=friend_request.id).status,
                         'rejected')
        mock_send_message.assert_called()

    def test_accept_friend_request_invalid_user(self):
        friend_request = FriendRequest.objects.create(sender_id=self.user1.id,
                                                      sender_username=self.user1.username,
                                                      receiver_id=self.user2.id,
                                                      receiver_username=self.user2.username)
        self.client.force_authenticate(user=self.user1)
        url = reverse('friendrequest-detail', kwargs={'id': friend_request.id})
        data = {'status': 'accepted'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'],
                         "You do not have permission to accept this request.")
