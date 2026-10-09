from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from stories.models import Story
from stories.tasks import deactivate_expired_stories

User = get_user_model()


def tiny_gif(name='story.gif'):
    return SimpleUploadedFile(
        name,
        b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
        b'\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
        b'\x00\x02\x02D\x01\x00;',
        content_type='image/gif',
    )


class Wave3StoryTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='story-owner@example.com', username='story_owner', password='StrongPass123!')
        self.other = User.objects.create_user(email='story-other@example.com', username='story_other', password='StrongPass123!')
        self.client.force_authenticate(user=self.owner)

    def test_story_crud_active_filter_and_unauthorized(self):
        create_response = self.client.post(
            '/api/v1/stories/',
            {'content': 'Hello story', 'visibility': 'public', 'media_file': tiny_gif()},
            format='multipart'
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        story_id = create_response.data['id']
        self.assertTrue(bool(create_response.data.get('media_url')))

        list_response = self.client.get('/api/v1/stories/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(list_response.data['count'], 1)

        retrieve_response = self.client.get(f'/api/v1/stories/{story_id}/')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.other)
        unauthorized_delete = self.client.delete(f'/api/v1/stories/{story_id}/')
        self.assertIn(unauthorized_delete.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        self.client.force_authenticate(user=self.owner)
        delete_response = self.client.delete(f'/api/v1/stories/{story_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_expired_story_is_filtered_from_active_surfaces(self):
        active_story = Story.objects.create(user=self.owner, content='active', visibility='public')
        expired_story = Story.objects.create(user=self.owner, content='expired', visibility='public')
        Story.objects.filter(id=expired_story.id).update(created_at=timezone.now() - timedelta(hours=25))

        deactivate_expired_stories()
        expired_story.refresh_from_db()
        active_story.refresh_from_db()

        self.assertFalse(expired_story.is_active)
        self.assertTrue(active_story.is_active)

        list_response = self.client.get('/api/v1/stories/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        ids = {item['id'] for item in list_response.data['results']}
        self.assertIn(str(active_story.id), ids)
        self.assertNotIn(str(expired_story.id), ids)

    def test_deactivate_expired_stories_is_idempotent(self):
        expired_story = Story.objects.create(user=self.owner, content='old', visibility='public')
        Story.objects.filter(id=expired_story.id).update(created_at=timezone.now() - timedelta(hours=25))

        first_run = deactivate_expired_stories()
        second_run = deactivate_expired_stories()
        expired_story.refresh_from_db()

        self.assertGreaterEqual(first_run, 1)
        self.assertEqual(second_run, 0)
        self.assertFalse(expired_story.is_active)
