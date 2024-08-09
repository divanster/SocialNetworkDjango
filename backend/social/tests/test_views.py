from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from social.models import Post
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

class PostViewSetTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_post(self):
        data = {
            'title': 'Test Post',
            'content': 'This is a test post.'
        }
        response = self.client.post(reverse('posts-list'), data, format='multipart')  # Use 'multipart'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Post')
        self.assertEqual(response.data['content'], 'This is a test post.')
    def test_create_post_unauthenticated(self):
        self.client.credentials()  # Clear the credentials to simulate an unauthenticated request
        data = {
            'title': 'Test Post',
            'content': 'This is a test post.'
        }
        response = self.client.post(reverse('posts-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
