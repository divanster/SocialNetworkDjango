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
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='This is a test post.'
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_post(self):
        data = {
            'title': 'New Post',
            'content': 'This is a new post.'
        }
        response = self.client.post(reverse('post-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_post(self):
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post(self):
        update_data = {'title': 'Updated Title'}
        response = self.client.patch(
            reverse('post-detail', kwargs={'pk': self.post.id}), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, update_data['title'])

    def test_delete_post(self):
        response = self.client.delete(
            reverse('post-detail', kwargs={'pk': self.post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
