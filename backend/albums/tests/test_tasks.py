# albums/tests/test_tasks.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from albums.models import Album
from albums.tasks import process_new_album
from unittest.mock import patch

User = get_user_model()

class AlbumTasksTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', username='testuser', password='password123'
        )
        self.album = Album.objects.create(user=self.user, title='Task Album')

    @patch('albums.tasks.SomeExternalService')
    def test_process_new_album(self, mock_service):
        # Simulate the external service
        mock_instance = mock_service.return_value
        mock_instance.process.return_value = True

        result = process_new_album(self.album.id)
        self.assertTrue(result)
        mock_instance.process.assert_called_once_with(self.album)
