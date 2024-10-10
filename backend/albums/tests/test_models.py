# albums/tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from albums.models import Album, Photo
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class AlbumModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', username='testuser', password='password123'
        )

    def test_album_creation(self):
        album = Album.objects.create(
            user=self.user,
            title='Vacation Photos',
            description='Photos from my vacation.'
        )
        self.assertEqual(album.title, 'Vacation Photos')
        self.assertEqual(album.description, 'Photos from my vacation.')
        self.assertEqual(album.user, self.user)
        self.assertEqual(str(album), 'Vacation Photos')

    def test_photo_creation(self):
        album = Album.objects.create(user=self.user, title='Test Album')
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x00\x00\x00\x00',
            content_type='image/jpeg'
        )
        photo = Photo.objects.create(
            album=album,
            image=image,
            description='A test photo.'
        )
        self.assertEqual(photo.album, album)
        self.assertEqual(photo.description, 'A test photo.')
        self.assertEqual(str(photo), f"Photo in {album.title}")
