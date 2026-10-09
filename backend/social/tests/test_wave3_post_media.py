from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from social.models import Post

User = get_user_model()


def tiny_gif(name='post.gif'):
    return SimpleUploadedFile(
        name,
        b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
        b'\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
        b'\x00\x02\x02D\x01\x00;',
        content_type='image/gif',
    )


class Wave3PostMediaTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='post-media@example.com', username='post_media', password='StrongPass123!')
        self.client.force_authenticate(user=self.user)

    def test_create_post_with_image_via_canonical_path(self):
        response = self.client.post(
            '/api/v1/social/',
            {
                'title': 'Post with image',
                'content': 'content',
                'visibility': 'public',
                'image_files': [tiny_gif()],
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=response.data['id'])
        self.assertEqual(post.images.count(), 1)
