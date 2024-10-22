from django.test import TestCase
from django.contrib.auth import get_user_model
from albums.models import Album
from albums.tasks import process_new_album
from unittest.mock import patch, MagicMock

User = get_user_model()

class AlbumTasksTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email='user@example.com', username='testuser', password='password123'
        )
        # Create a test album
        self.album = Album.objects.create(user_id=self.user.id, user_username=self.user.username, title='Task Album')

    @patch('albums.tasks.SomeExternalService')
    def test_process_new_album(self, mock_service):
        # Create a mock instance of the external service
        mock_instance = mock_service.return_value
        mock_instance.process.return_value = True

        # Call the task synchronously for the test
        result = process_new_album(self.album.id)

        # Assert the expected result
        self.assertTrue(result)

        # Assert that the external service was called with the album instance
        mock_instance.process.assert_called_once_with(self.album)

    @patch('albums.tasks.process_new_album.delay', MagicMock())
    def test_task_is_called_async(self):
        # Verify if the Celery task is being called asynchronously
        from albums.views import AlbumViewSet

        # Use a mock request
        request = MagicMock()
        request.user = self.user

        # Mock the serializer save and trigger the viewset method
        album_viewset = AlbumViewSet()
        album_viewset.perform_create = MagicMock()

        # Simulate performing album creation
        album_viewset.perform_create(request)

        # Assert that the Celery task has been called asynchronously
        process_new_album.delay.assert_called_once_with(self.album.id)
