from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from albums.models import Album, Photo

User = get_user_model()


def tiny_gif(name='image.gif'):
    return SimpleUploadedFile(
        name,
        b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
        b'\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
        b'\x00\x02\x02D\x01\x00;',
        content_type='image/gif',
    )


class Wave3AlbumPhotoTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='album-owner@example.com', username='album_owner', password='StrongPass123!')
        self.other = User.objects.create_user(email='album-other@example.com', username='album_other', password='StrongPass123!')
        self.client.force_authenticate(user=self.owner)

    def test_album_crud_and_owner_rules(self):
        create_response = self.client.post(
            '/api/v1/albums/',
            {'title': 'Summer', 'description': 'Trip', 'visibility': 'public', 'image_files': [tiny_gif()]},
            format='multipart'
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        album_id = create_response.data['id']
        self.assertEqual(len(create_response.data['photos']), 1)

        list_response = self.client.get('/api/v1/albums/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(list_response.data['count'], 1)

        retrieve_response = self.client.get(f'/api/v1/albums/{album_id}/')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data['title'], 'Summer')

        update_response = self.client.patch(
            f'/api/v1/albums/{album_id}/',
            {'title': 'Summer Edited', 'image_files': [tiny_gif('new.gif')]},
            format='multipart'
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['title'], 'Summer Edited')
        self.assertEqual(len(update_response.data['photos']), 2)

        self.client.force_authenticate(user=self.other)
        unauthorized_response = self.client.patch(
            f'/api/v1/albums/{album_id}/',
            {'title': 'Hacked'},
            format='multipart'
        )
        self.assertIn(unauthorized_response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        self.client.force_authenticate(user=self.owner)
        delete_response = self.client.delete(f'/api/v1/albums/{album_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Album.all_objects.get(id=album_id).is_deleted)

    def test_photo_upload_list_retrieve_delete_and_invalid_album(self):
        album = Album.objects.create(user=self.owner, title='Photo album', description='desc', visibility='public')
        upload_response = self.client.post(
            '/api/v1/albums/photos/',
            {'album': str(album.id), 'image': tiny_gif(), 'description': 'caption'},
            format='multipart'
        )
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        photo_id = upload_response.data['id']

        list_response = self.client.get(f'/api/v1/albums/photos/?album={album.id}')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)

        retrieve_response = self.client.get(f'/api/v1/albums/photos/{photo_id}/')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.other)
        wrong_owner_delete = self.client.delete(f'/api/v1/albums/photos/{photo_id}/')
        self.assertIn(wrong_owner_delete.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        self.client.force_authenticate(user=self.owner)
        delete_response = self.client.delete(f'/api/v1/albums/photos/{photo_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Photo.all_objects.get(id=photo_id).is_deleted)

        invalid_album_response = self.client.post(
            '/api/v1/albums/photos/',
            {'album': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'image': tiny_gif()},
            format='multipart'
        )
        self.assertEqual(invalid_album_response.status_code, status.HTTP_400_BAD_REQUEST)
