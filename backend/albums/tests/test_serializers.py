from django.test import TestCase
from django.contrib.auth import get_user_model
from albums.models import Album, Photo
from albums.serializers import AlbumSerializer, PhotoSerializer
from rest_framework.test import APIRequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from mongoengine import NotUniqueError

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
        # Create two images to be uploaded
        image1 = SimpleUploadedFile("test1.jpg", b"file_content1",
                                    content_type="image/jpeg")
        image2 = SimpleUploadedFile("test2.jpg", b"file_content2",
                                    content_type="image/jpeg")

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

        # Validate and save the serializer, asserting the serializer is valid
        self.assertTrue(serializer.is_valid(), serializer.errors)
        album = serializer.save(user=self.user)

        # Assertions to verify album creation
        self.assertEqual(album.title, 'New Album')
        self.assertEqual(album.description, 'An awesome album')
        self.assertEqual(album.user_id,
                         self.user.id)  # Ensure the user is correctly set

        # Assertions for the related photos
        photos = Photo.objects(album=album)
        self.assertEqual(photos.count(), 2)
        self.assertEqual(photos[0].description, 'First photo')
        self.assertEqual(photos[1].description, 'Second photo')

    def test_album_serializer_update(self):
        # Create an album
        album = Album.objects.using('social_db').create(user_id=self.user.id,
                                                        user_username=self.user.username,
                                                        title='Initial Album')

        # Create a photo associated with the album
        photo = Photo.objects.using('social_db').create(
            album=album,
            image=SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg"),
            description='Initial photo'
        )

        # Updated data for the album, modifying its title and updating the photo description
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

        # Validate and save the serializer, asserting the serializer is valid
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_album = serializer.save()

        # Assertions for the album update
        self.assertEqual(updated_album.title, 'Updated Album')

        # Refresh the photo from the database and assert its updated description
        photo.refresh_from_db()
        self.assertEqual(photo.description, 'Updated photo')

        # Check the soft delete status
        self.assertFalse(album.is_deleted)

    def test_album_with_duplicate_title(self):
        # Create an album
        album = Album.objects.using('social_db').create(user_id=self.user.id,
                                                        user_username=self.user.username,
                                                        title='Unique Title')

        # Try to create another album with the same title for the same user
        try:
            duplicate_album = Album.objects.using('social_db').create(
                user_id=self.user.id, user_username=self.user.username,
                title='Unique Title')
            self.fail("Expected a NotUniqueError but it didn't occur")
        except NotUniqueError:
            pass

        # Assert that only one album with the title exists
        album_count = Album.objects(user_id=self.user.id, title='Unique Title').count()
        self.assertEqual(album_count, 1)
