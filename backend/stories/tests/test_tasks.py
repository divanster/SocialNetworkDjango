from django.test import TestCase
from stories.tasks import send_story_event_to_kafka
from unittest.mock import patch, MagicMock
from stories.models import Story

class TestStoryTasks(TestCase):

    @patch('kafka_app.producer.KafkaProducerClient.send_message')
    def test_send_story_event_to_kafka(self, mock_send_message):
        story = Story.objects.create(
            user_id=1,
            user_username="test_user",
            content="This is a test story"
        )

        send_story_event_to_kafka(story.id, 'created')

        expected_message = {
            "story_id": story.id,
            "user_id": story.user_id,
            "content": story.content,
            "created_at": str(story.created_at),
            "event": 'created'
        }

        mock_send_message.assert_called_once_with('STORY_EVENTS', expected_message)

    @patch('kafka_app.producer.KafkaProducerClient.send_message')
    def test_send_story_event_to_kafka_deleted(self, mock_send_message):
        story_id = 1
        send_story_event_to_kafka(story_id, 'deleted')

        expected_message = {
            "story_id": story_id,
            "event": "deleted"
        }

        mock_send_message.assert_called_once_with('STORY_EVENTS', expected_message)
