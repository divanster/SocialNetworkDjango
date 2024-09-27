# backend/social/tests/test_views.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from social.models import Post, PostImage
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class PostViewSetTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='viewuser@example.com',
            username='viewuser',
            password='viewpassword'
        )
        self.client.force_authenticate(user=self.user)
        self.post = Post.objects.create(
            title='View Post',
            content='Content for view post.',
            author=self.user
        )

    def test_list_posts(self):
        url = reverse('post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'View Post')

    def test_create_post(self):
        url = reverse('post-list')
        image = SimpleUploadedFile('test_image.jpg', b'file_content',
                                   content_type='image/jpeg')
        data = {
            'title': 'New Post',
            'content': 'New content',
            'image_files': [image],
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        new_post = Post.objects.get(title='New Post')
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.images.count(), 1)

    def test_retrieve_post(self):
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'View Post')

    def test_update_post(self):
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_delete_post(self):
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_unauthenticated_create_post(self):
        self.client.logout()
        url = reverse('post-list')
        data = {'title': 'Unauthorized Post', 'content': 'No auth'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
