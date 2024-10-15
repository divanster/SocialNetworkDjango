from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch
from social.models import Post, PostImage
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class PostViewSetTest(APITestCase):

    def setUp(self):
        # Set up a user and authenticate
        self.user = User.objects.create_user(
            username='testuser', email='user@example.com', password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # Set up a second user for permissions testing
        self.other_user = User.objects.create_user(
            username='otheruser', email='other@example.com', password='password123'
        )
        self.post_data = {
            'title': 'Test Post',
            'content': 'This is a test post.',
            'image_files': [
                SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
            ],
            'tagged_user_ids': [self.other_user.id]
        }

    @patch('social.tasks.process_new_post.delay')
    def test_create_post(self, mock_process_new_post):
        # Test creating a new post
        url = reverse('post-list')
        response = self.client.post(url, self.post_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

        post = Post.objects.first()
        self.assertEqual(post.title, self.post_data['title'])
        self.assertEqual(post.content, self.post_data['content'])
        self.assertEqual(post.author.id, self.user.id)

        # Check if image was uploaded
        self.assertEqual(post.images.count(), 1)

        # Check if the Celery task was triggered
        mock_process_new_post.assert_called_once_with(post.id)

    @patch('social.tasks.process_new_post.delay')
    def test_create_post_with_invalid_data(self, mock_process_new_post):
        # Test creating a post with invalid data
        invalid_data = {
            'title': '',  # Empty title should trigger validation error
            'content': 'Test content',
        }
        url = reverse('post-list')
        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Post.objects.count(), 0)
        mock_process_new_post.assert_not_called()

    def test_retrieve_post(self):
        # Test retrieving a single post
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author_id=self.user.id,
            author_username=self.user.username,
        )
        url = reverse('post-detail', kwargs={'pk': post.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], post.title)
        self.assertEqual(response.data['content'], post.content)

    def test_list_posts(self):
        # Create multiple posts to test listing
        Post.objects.create(
            title='Post 1', content='Content 1', author_id=self.user.id, author_username=self.user.username
        )
        Post.objects.create(
            title='Post 2', content='Content 2', author_id=self.other_user.id, author_username=self.other_user.username
        )

        url = reverse('post-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Post 2')  # Ordered by created_at

    def test_update_post(self):
        # Test updating a post by the author
        post = Post.objects.create(
            title='Old Title',
            content='Old content.',
            author_id=self.user.id,
            author_username=self.user.username
        )
        updated_data = {'title': 'Updated Title', 'content': 'Updated content.'}
        url = reverse('post-detail', kwargs={'pk': post.pk})
        response = self.client.patch(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, 'Updated Title')
        self.assertEqual(post.content, 'Updated content')

    def test_update_post_not_author(self):
        # Test trying to update a post by someone other than the author
        post = Post.objects.create(
            title='Old Title',
            content='Old content.',
            author_id=self.user.id,
            author_username=self.user.username
        )
        self.client.force_authenticate(user=self.other_user)
        updated_data = {'title': 'Updated Title'}
        url = reverse('post-detail', kwargs={'pk': post.pk})
        response = self.client.patch(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post(self):
        # Test deleting a post by the author
        post = Post.objects.create(
            title='To be deleted',
            content='Content of post to be deleted.',
            author_id=self.user.id,
            author_username=self.user.username
        )
        url = reverse('post-detail', kwargs={'pk': post.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_post_not_author(self):
        # Test trying to delete a post by someone other than the author
        post = Post.objects.create(
            title='To be deleted',
            content='Content of post to be deleted.',
            author_id=self.user.id,
            author_username=self.user.username
        )
        self.client.force_authenticate(user=self.other_user)
        url = reverse('post-detail', kwargs={'pk': post.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)

    def test_unauthenticated_user_create_post(self):
        # Test creating a post without being authenticated
        self.client.logout()
        url = reverse('post-list')
        response = self.client.post(url, self.post_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Post.objects.count(), 0)

    def test_authenticated_user_get_posts(self):
        # Test that an authenticated user can retrieve a list of posts
        Post.objects.create(
            title='Post 1', content='Content 1', author_id=self.user.id, author_username=self.user.username
        )
        url = reverse('post-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_partial_update_post_image(self):
        # Test updating a post by adding an image
        post = Post.objects.create(
            title='Old Title',
            content='Old content.',
            author_id=self.user.id,
            author_username=self.user.username
        )
        updated_data = {
            'image_files': [SimpleUploadedFile("new_image.jpg", b"new_file_content", content_type="image/jpeg")]
        }
        url = reverse('post-detail', kwargs={'pk': post.pk})
        response = self.client.patch(url, updated_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.images.count(), 1)
