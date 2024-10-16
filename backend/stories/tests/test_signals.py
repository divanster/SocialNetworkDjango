from django.test import TestCase
from stories.models import Story
from stories.tasks import send_story_event_to_kafka
from unittest.mock import patch


class TestStorySignals(TestCase):

    @patch('stories.signals.send_story_event_to_kafka.delay')
    def test_story_created_signal(self, mock_send_event):
        story = Story.objects.create(
            user_id=1,
            user_username="test_user",
            content="This is a test story"
        )

        mock_send_event.assert_called_once_with(story.id, 'created')

    @patch('stories.signals.send_story_event_to_kafka.delay')
    def test_story_deleted_signal(self, mock_send_event):
        story = Story.objects.create(
            user_id=1,
            user_username="test_user",
            content="This is a test story"
        )
        story.delete()

        mock_send_event.assert_called_once_with(story.id, 'deleted')
