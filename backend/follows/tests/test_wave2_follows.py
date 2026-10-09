from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from follows.models import Follow

User = get_user_model()


class Wave2FollowTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(email='follow-a@example.com', username='follow_a', password='StrongPass123!')
        self.user_b = User.objects.create_user(email='follow-b@example.com', username='follow_b', password='StrongPass123!')
        self.client.force_authenticate(user=self.user_a)

    def test_create_follow_success(self):
        response = self.client.post('/api/v1/follows/', {'followed': str(self.user_b.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.filter(follower=self.user_a, followed=self.user_b).count(), 1)

    def test_create_follow_duplicate_rejected(self):
        Follow.objects.create(follower=self.user_a, followed=self.user_b)
        response = self.client.post('/api/v1/follows/', {'followed': str(self.user_b.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_follow_self_rejected(self):
        response = self.client.post('/api/v1/follows/', {'followed': str(self.user_a.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_follow_with_user_id_alias(self):
        response = self.client.post('/api/v1/follows/', {'user_id': str(self.user_b.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unfollow_success(self):
        create_response = self.client.post('/api/v1/follows/', {'followed': str(self.user_b.id)}, format='json')
        follow_id = create_response.data['id']
        delete_response = self.client.delete(f'/api/v1/follows/{follow_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthorized_behavior(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/v1/follows/', {'followed': str(self.user_b.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
