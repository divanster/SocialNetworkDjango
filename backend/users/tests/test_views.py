from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from social.models import Post
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class PostViewSetTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_post(self):
        data = {
            'title': 'New Post',
            'content': 'This is a new post.'
        }
        # Corrected to match the registered basename 'posts'
        response = self.client.post(reverse('posts-list'), data)  # Updated 'post-list' to 'posts-list'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'New Post')

    def test_get_post(self):
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user
        )
        response = self.client.get(reverse('posts-detail', kwargs={'pk': post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post(self):
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user
        )
        update_data = {'title': 'Updated Title'}
        response = self.client.patch(reverse('posts-detail', kwargs={'pk': post.id}), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, update_data['title'])

    def test_delete_post(self):
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user
        )
        response = self.client.delete(reverse('posts-detail', kwargs={'pk': post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
