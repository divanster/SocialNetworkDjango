from django.test import TestCase
from django.contrib.auth import get_user_model
from albums.models import Album, Photo
from albums.serializers import AlbumSerializer, PhotoSerializer
from rest_framework.test import APIRequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class AlbumSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', username='testuser', password='password123'
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.post('/albums/')
        self.request.user = self.user

    def test_album_serializer_create(self):
        image1 = SimpleUploadedFile("test1.jpg", b"file_content1", content_type="image/jpeg")
        image2 = SimpleUploadedFile("test2.jpg", b"file_content2", content_type="image/jpeg")
        data = {
            'title': 'New Album',
            'description': 'An awesome album',
            'photos_upload': [
                {'image': image1, 'description': 'First photo'},
                {'image': image2, 'description': 'Second photo'}
            ],
            'tagged_user_ids': []
        }
        serializer = AlbumSerializer(
            data=data, context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        album = serializer.save(user=self.user)
        self.assertEqual(album.title, 'New Album')
        self.assertEqual(album.photos.count(), 2)
        self.assertEqual(album.photos.first().description, 'First photo')

    def test_album_serializer_update(self):
        album = Album.objects.using('social_db').create(user=self.user, title='Initial Album')
        photo = Photo.objects.using('social_db').create(
            album=album,
            image=SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg"),
            description='Initial photo'
        )

        data = {
            'title': 'Updated Album',
            'photos_upload': [
                {'id': photo.id, 'description': 'Updated photo'}
            ],
            'tagged_user_ids': []
        }
        serializer = AlbumSerializer(
            album, data=data, partial=True, context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_album = serializer.save()
        self.assertEqual(updated_album.title, 'Updated Album')
        photo.refresh_from_db()
        self.assertEqual(photo.description, 'Updated photo')
