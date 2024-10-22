from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from albums.models import Album, Photo
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

User = get_user_model()


class AlbumViewSetTest(TestCase):
    """
    Test case for CRUD operations related to AlbumViewSet. This includes:
    creating an album, retrieving an album, listing albums, updating an album,
    and deleting an album. Mocks are used to simulate external task handling.
    """

    def setUp(self):
        """
        Set up the initial state for tests.
        - Create a test user.
        - Authenticate the client with the created user to simulate logged-in behavior.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@example.com', username='testuser', password='password123'
        )
        # Force authentication for the API client
        self.client.force_authenticate(user=self.user)

    @patch('albums.tasks.process_new_album.delay')
    def test_create_album(self, mock_process_new_album_delay):
        """
        Test creating a new album.
        - Ensure the album is successfully created.
        - Validate that the Celery task is called to process the new album.
        """
        url = reverse('albums:album-list')

        # Create a mock image to upload
        image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")

        # Payload to create an album with photos
        data = {
            'title': 'My Album',
            'description': 'Test album',
            'photos_upload': [
                {'image': image, 'description': 'A photo'}
            ],
            'tagged_user_ids': []  # This could be updated later to include actual
            # tagged users
        }

        # Send POST request to create the album
        response = self.client.post(url, data, format='multipart')

        # Assert that the response status code is 201 CREATED
        self.assertEqual(response.status_code, 201)

        # Retrieve the created album and validate its properties
        album = Album.objects.using('social_db').get(title='My Album')
        self.assertEqual(album.user, self.user)

        # Verify that the task to process the new album has been called
        mock_process_new_album_delay.assert_called_once_with(album.id)

    def test_retrieve_album(self):
        """
        Test retrieving a specific album by its ID.
        - Ensure that the correct album details are returned.
        """
        # Create a new album to retrieve later
        album = Album.objects.using('social_db').create(user=self.user,
                                                        title='My Album')

        # Generate the URL for retrieving the specific album
        url = reverse('albums:album-detail', kwargs={'pk': album.pk})

        # Send GET request to retrieve the album
        response = self.client.get(url)

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Validate that the album details match the expected values
        self.assertEqual(response.data['title'], 'My Album')

    def test_list_albums(self):
        """
        Test listing all albums for the authenticated user.
        - Ensure the correct number of albums is returned.
        """
        # Create multiple albums for the user
        Album.objects.using('social_db').create(user=self.user, title='Album 1')
        Album.objects.using('social_db').create(user=self.user, title='Album 2')

        # Generate the URL for listing all albums
        url = reverse('albums:album-list')

        # Send GET request to retrieve the list of albums
        response = self.client.get(url)

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Verify that two albums were returned in the response
        self.assertEqual(len(response.data), 2)

    def test_update_album(self):
        """
        Test updating an existing album.
        - Ensure that the album's title is updated correctly.
        """
        # Create an album with an initial title
        album = Album.objects.using('social_db').create(user=self.user,
                                                        title='Old Title')

        # Generate the URL for updating the album
        url = reverse('albums:album-detail', kwargs={'pk': album.pk})

        # Payload to update the title of the album
        data = {'title': 'New Title'}

        # Send PATCH request to update the album
        response = self.client.patch(url, data, format='json')

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Refresh the album instance from the database and verify the new title
        album.refresh_from_db()
        self.assertEqual(album.title, 'New Title')

    def test_delete_album(self):
        """
        Test deleting an existing album.
        - Ensure that the album is removed from the database.
        """
        # Create an album to be deleted
        album = Album.objects.using('social_db').create(user=self.user,
                                                        title='To Delete')

        # Generate the URL for deleting the album
        url = reverse('albums:album-detail', kwargs={'pk': album.pk})

        # Send DELETE request to remove the album
        response = self.client.delete(url)

        # Assert that the response status code is 204 NO CONTENT
        self.assertEqual(response.status_code, 204)

        # Verify that the album no longer exists in the database
        self.assertFalse(Album.objects.using('social_db').filter(pk=album.pk).exists())

    def tearDown(self):
        """
        Tear down any state that was previously set up with `setUp()`.
        - Remove all album and photo records to ensure test isolation.
        """
        Album.objects.using('social_db').delete()
        Photo.objects.using('social_db').delete()
