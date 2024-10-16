from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from stories.models import Story
from django.contrib.auth import get_user_model

User = get_user_model()

class TestStoryViewSet(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.story_url = reverse('stories:story-list')

    def test_create_story(self):
        data = {
            'content': 'This is a new story',
            'tagged_user_ids': []
        }

        response = self.client.post(self.story_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Story.objects.count(), 1)
        self.assertEqual(Story.objects.first().content, 'This is a new story')

    def test_update_story(self):
        story = Story.objects.create(
            user_id=self.user.id,
            user_username=self.user.username,
            content='Old content'
        )

        data = {
            'content': 'Updated content'
        }

        url = reverse('stories:story-detail', args=[story.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        story.refresh_from_db()
        self.assertEqual(story.content, 'Updated content')

    def test_delete_story(self):
        story = Story.objects.create(
            user_id=self.user.id,
            user_username=self.user.username,
            content='Story to delete'
        )

        url = reverse('stories:story-detail', args=[story.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Story.objects.count(), 0)
