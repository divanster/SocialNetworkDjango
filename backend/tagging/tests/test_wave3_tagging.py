from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification
from social.models import Post
from tagging.models import TaggedItem

User = get_user_model()


class Wave3TaggingTests(APITestCase):
    def setUp(self):
        self.tagger = User.objects.create_user(email='tagger@example.com', username='tagger', password='StrongPass123!')
        self.tagged = User.objects.create_user(email='tagged@example.com', username='tagged', password='StrongPass123!')
        self.other = User.objects.create_user(email='other@example.com', username='other', password='StrongPass123!')
        self.post = Post.objects.create(user=self.tagger, title='Tag target', content='content', visibility='public')
        self.content_type = ContentType.objects.get_for_model(Post)
        self.client.force_authenticate(user=self.tagger)

    def test_create_tag_and_list(self):
        response = self.client.post(
            '/api/v1/tagging/',
            {
                'content_type': self.content_type.id,
                'object_id': str(self.post.id),
                'tagged_user_id': str(self.tagged.id),
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaggedItem.objects.count(), 1)

        list_response = self.client.get('/api/v1/tagging/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)

    def test_duplicate_invalid_user_invalid_object(self):
        payload = {
            'content_type': self.content_type.id,
            'object_id': str(self.post.id),
            'tagged_user_id': str(self.tagged.id),
        }
        self.client.post('/api/v1/tagging/', payload, format='json')
        duplicate_response = self.client.post('/api/v1/tagging/', payload, format='json')
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_user_response = self.client.post(
            '/api/v1/tagging/',
            {
                'content_type': self.content_type.id,
                'object_id': str(self.post.id),
                'tagged_user_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            },
            format='json'
        )
        self.assertEqual(invalid_user_response.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_object_response = self.client.post(
            '/api/v1/tagging/',
            {
                'content_type': self.content_type.id,
                'object_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                'tagged_user_id': str(self.tagged.id),
            },
            format='json'
        )
        self.assertEqual(invalid_object_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_tag_supported_and_notification_does_not_crash(self):
        create_response = self.client.post(
            '/api/v1/tagging/',
            {
                'content_type': self.content_type.id,
                'object_id': str(self.post.id),
                'tagged_user_id': str(self.tagged.id),
            },
            format='json'
        )
        tag_id = create_response.data['id']

        self.client.force_authenticate(user=self.tagged)
        delete_response = self.client.delete(f'/api/v1/tagging/{tag_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        notification = Notification.objects.filter(receiver=self.tagged).first()
        self.assertIsNotNone(notification)
        self.client.force_authenticate(user=self.tagged)
        notification_list = self.client.get('/api/v1/notifications/')
        self.assertEqual(notification_list.status_code, status.HTTP_200_OK)

    def test_unauthorized_behavior(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            '/api/v1/tagging/',
            {
                'content_type': self.content_type.id,
                'object_id': str(self.post.id),
                'tagged_user_id': str(self.other.id),
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
