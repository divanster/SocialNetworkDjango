from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from albums.models import Album, Photo
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

User = get_user_model()


class AlbumViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@example.com', username='testuser', password='password123'
        )
        self.client.force_authenticate(user=self.user)

    @patch('albums.tasks.process_new_album.delay')
    def test_create_album(self, mock_process_new_album_delay):
        url = reverse('albums:album-list')
        image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        data = {
            'title': 'My Album',
            'description': 'Test album',
            'photos_upload': [
                {'image': image, 'description': 'A photo'}
            ],
            'tagged_user_ids': []
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 201)
        album = Album.objects.using('social_db').get(title='My Album')
        self.assertEqual(album.user, self.user)
        mock_process_new_album_delay.assert_called_once_with(album.id)

    def test_retrieve_album(self):
        album = Album.objects.using('social_db').create(user=self.user, title='My Album')
        url = reverse('albums:album-detail', kwargs={'pk': album.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'My Album')

    def test_list_albums(self):
        Album.objects.using('social_db').create(user=self.user, title='Album 1')
        Album.objects.using('social_db').create(user=self.user, title='Album 2')
        url = reverse('albums:album-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_update_album(self):
        album = Album.objects.using('social_db').create(user=self.user, title='Old Title')
        url = reverse('albums:album-detail', kwargs={'pk': album.pk})
        data = {'title': 'New Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        album.refresh_from_db()
        self.assertEqual(album.title, 'New Title')

    def test_delete_album(self):
        album = Album.objects.using('social_db').create(user=self.user, title='To Delete')
        url = reverse('albums:album-detail', kwargs={'pk': album.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Album.objects.using('social_db').filter(pk=album.pk).exists())
