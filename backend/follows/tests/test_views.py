from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from follows.models import Follow
from unittest.mock import patch

User = get_user_model()


class FollowViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')
        self.client.force_authenticate(user=self.user1)

    @patch('follows.views.KafkaProducerClient.send_message')
    def test_create_follow(self, mock_send_message):
        url = reverse('follow-list')
        data = {
            'followed': self.user2.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 1)
        mock_send_message.assert_called_once()

    @patch('follows.views.KafkaProducerClient.send_message')
    def test_delete_follow(self, mock_send_message):
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)
        url = reverse('follow-detail', kwargs={'pk': follow.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Follow.objects.count(), 0)
        mock_send_message.assert_called_once()
