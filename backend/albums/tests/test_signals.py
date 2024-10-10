# albums/tests/test_signals.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from albums.models import Album, Photo
from tagging.models import TaggedItem
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class AlbumSavedSignalTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', username='testuser', password='password123'
        )

    @patch('albums.handlers.KafkaProducerClient')
    def test_album_created_signal(self, mock_kafka_producer):
        # Mock the Kafka producer instance
        mock_producer_instance = mock_kafka_producer.return_value
        album = Album.objects.create(
            user=self.user,
            title='Test Album',
            description='A description'
        )
        # Verify that send_message was called with correct parameters
        expected_message = {
            'event': 'created',
            'album': str(album.id),
            'title': 'Test Album',
            'description': 'A description',
            'tagged_user_ids': [],
        }
        mock_producer_instance.send_message.assert_called_once_with('ALBUM_EVENTS',
                                                                    expected_message)

    @patch('albums.handlers.KafkaProducerClient')
    def test_album_updated_signal(self, mock_kafka_producer):
        # Create an album
        album = Album.objects.create(
            user=self.user,
            title='Initial Title',
            description='Initial Description'
        )
        mock_producer_instance = mock_kafka_producer.return_value
        mock_producer_instance.send_message.reset_mock()
        # Update the album
        album.title = 'Updated Title'
        album.save()
        # Verify that send_message was called with correct parameters
        expected_message = {
            'event': 'updated',
            'album': str(album.id),
            'title': 'Updated Title',
            'description': 'Initial Description',
            'tagged_user_ids': [],
        }
        mock_producer_instance.send_message.assert_called_once_with('ALBUM_EVENTS',
                                                                    expected_message)


    @patch('albums.handlers.KafkaProducerClient')
    def test_album_saved_with_tagged_users(self, mock_kafka_producer):
        # Create tagged users
        tagged_user1 = User.objects.create_user(
            email='tagged1@example.com', username='taggeduser1', password='password123'
        )
        tagged_user2 = User.objects.create_user(
            email='tagged2@example.com', username='taggeduser2', password='password123'
        )
        album = Album.objects.create(
            user=self.user,
            title='Tagged Album',
            description='Album with tags'
        )
        # Create TaggedItems
        content_type = ContentType.objects.get_for_model(Album)
        TaggedItem.objects.create(
            content_type=content_type,
            object_id=album.id,
            tagged_user=tagged_user1,
            tagged_by=self.user
        )
        TaggedItem.objects.create(
            content_type=content_type,
            object_id=album.id,
            tagged_user=tagged_user2,
            tagged_by=self.user
        )
        # Save the album to trigger the signal
        album.save()
        # Verify the message includes tagged user IDs
        expected_tagged_user_ids = [str(tagged_user1.id), str(tagged_user2.id)]
        expected_message = {
            'event': 'updated',  # Since the album already exists
            'album': str(album.id),
            'title': 'Tagged Album',
            'description': 'Album with tags',
            'tagged_user_ids': expected_tagged_user_ids,
        }
        mock_producer_instance = mock_kafka_producer.return_value
        mock_producer_instance.send_message.assert_called_once_with('ALBUM_EVENTS', expected_message)

    @patch('albums.handlers.KafkaProducerClient')
    def test_album_deleted_signal(self, mock_kafka_producer):
        album = Album.objects.create(
            user=self.user,
            title='To Be Deleted',
            description='This album will be deleted'
        )
        mock_producer_instance = mock_kafka_producer.return_value
        # Delete the album
        album.delete()
        # Verify that send_message was called with correct parameters
        expected_message = {
            'event': 'deleted',
            'album': str(album.id),
            'title': 'To Be Deleted',
            'description': 'This album will be deleted',
            'tagged_user_ids': [],
        }
        mock_producer_instance.send_message.assert_called_once_with('ALBUM_EVENTS', expected_message)

    class PhotoSavedSignalTest(TestCase):

        def setUp(self):
            self.user = User.objects.create_user(
                email='user@example.com', username='testuser', password='password123'
            )
            self.album = Album.objects.create(
                user=self.user,
                title='Test Album',
                description='Album for testing photos'
            )

        @patch('albums.handlers.KafkaProducerClient')
        def test_photo_created_signal(self, mock_kafka_producer):
            mock_producer_instance = mock_kafka_producer.return_value
            photo = Photo.objects.create(
                album=self.album,
                image=SimpleUploadedFile("test.jpg", b"content",
                                         content_type="image/jpeg"),
                description='Test Photo'
            )
            expected_message = {
                'event': 'created',
                'photo_id': str(photo.id),
                'album_id': str(self.album.id),
                'description': 'Test Photo',
                'image_path': photo.image.url,
            }
            mock_producer_instance.send_message.assert_called_once_with('PHOTO_EVENTS',
                                                                        expected_message)

        @patch('albums.handlers.KafkaProducerClient')
        def test_photo_updated_signal(self, mock_kafka_producer):
            photo = Photo.objects.create(
                album=self.album,
                image=SimpleUploadedFile("test.jpg", b"content",
                                         content_type="image/jpeg"),
                description='Initial Description'
            )
            mock_producer_instance = mock_kafka_producer.return_value
            mock_producer_instance.send_message.reset_mock()
            # Update the photo
            photo.description = 'Updated Description'
            photo.save()
            expected_message = {
                'event': 'updated',
                'photo_id': str(photo.id),
                'album_id': str(self.album.id),
                'description': 'Updated Description',
                'image_path': photo.image.url,
            }
            mock_producer_instance.send_message.assert_called_once_with('PHOTO_EVENTS',
                                                                        expected_message)

    @patch('albums.handlers.KafkaProducerClient')
    def test_photo_deleted_signal(self, mock_kafka_producer):
        photo = Photo.objects.create(
            album=self.album,
            image=SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg"),
            description='To be deleted'
        )
        mock_producer_instance = mock_kafka_producer.return_value
        # Delete the photo
        photo.delete()
        expected_message = {
            'event': 'deleted',
            'photo_id': str(photo.id),
            'album_id': str(self.album.id),
        }
        mock_producer_instance.send_message.assert_called_once_with('PHOTO_EVENTS', expected_message)
