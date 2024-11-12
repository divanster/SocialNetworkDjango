from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from social.models import Post
from django.core.files.uploadedfile import SimpleUploadedFile


class PostViewSetTest(APITestCase):

    def setUp(self):
        # Create two users for testing with both username and email
        self.user_1 = get_user_model().objects.create_user(
            email='user1@example.com',
            username='user1',
            password='password'
        )
        self.user_2 = get_user_model().objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password'
        )

        # Create a post for testing purposes
        self.post_data = {
            'title': 'Test Post',
            'content': 'Test Content',
            'visibility': 'public'
        }
        self.post = Post.objects.create(
            title="Existing Post",
            content="This is an existing post",
            author=self.user_1
        )

    def get_authentication_headers(self, user):
        """
        Helper method to get the Authorization header with a valid JWT token.
        """
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        return {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

    def test_create_post_authenticated(self):
        # Test creating a post with an authenticated user (user_1)
        url = '/api/v1/social/'  # Adjust this to the correct URL for your Post API
        headers = self.get_authentication_headers(self.user_1)

        # Send a POST request to create a post (in JSON format)
        response = self.client.post(url, self.post_data, **headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_post_with_invalid_data(self):
        # Test creating a post with invalid data
        url = '/api/v1/social/'  # Adjust this to the correct URL for your Post API
        headers = self.get_authentication_headers(self.user_1)

        # Invalid data (missing title)
        invalid_data = {'content': 'Test Content', 'visibility': 'public'}

        response = self.client.post(url, invalid_data, **headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_post_with_image(self):
        # Test creating a post with an image (multipart/form-data)
        url = '/api/v1/social/'  # Adjust this to the correct URL for your Post API
        headers = self.get_authentication_headers(self.user_1)

        # Create a mock image using SimpleUploadedFile
        image_file = SimpleUploadedFile("test_image.jpg", b"file_content",
                                        content_type="image/jpeg")

        data = {
            'title': 'Post with Image',
            'content': 'This post has an image.',
            'visibility': 'public',
            'image': image_file,
        }
        response = self.client.post(url, data, **headers, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_post_authenticated(self):
        # Test updating a post with an authenticated user
        url = f'/api/v1/social/{self.post.id}/'  # Adjust the URL to point to the specific post
        headers = self.get_authentication_headers(self.user_1)

        # Update data
        updated_data = {'title': 'Updated Title', 'content': 'Updated Content',
                        'visibility': 'public'}
        response = self.client.patch(url, updated_data, **headers, format='json')

        # Assert the post was updated correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_delete_post(self):
        # Test deleting a post by the author
        url = f'/api/v1/social/{self.post.id}/'  # Adjust the URL to point to the specific post
        headers = self.get_authentication_headers(self.user_1)

        # Delete the post as the author (user_1)
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the post is soft deleted (marking it as deleted instead of removing it from DB)
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_deleted)  # Check that 'is_deleted' flag is True
