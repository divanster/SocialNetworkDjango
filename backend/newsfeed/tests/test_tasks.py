from django.test import TestCase
from unittest.mock import patch
from social.models import Post
from django.contrib.auth import get_user_model
from newsfeed.tasks import send_newsfeed_event_to_kafka

User = get_user_model()


class TestNewsfeedTasks(TestCase):
    @patch('newsfeed.tasks.KafkaProducerClient.send_message')
    def test_send_newsfeed_event_to_kafka(self, mock_send_message):
        user = User.objects.create_user(username='testuser', email='test@example.com',
                                        password='password')
        post = Post.objects.create(author=user, title='Test Post',
                                   content='Test Content')

        # Call the task function
        send_newsfeed_event_to_kafka(post.id, 'created', 'Post')

        # Verify that send_message was called with the correct topic and data
        mock_send_message.assert_called_once_with(
            'NEWSFEED_EVENTS', {
                'id': post.id,
                'event_type': 'created',
                'model_name': 'Post',
                'data': {
                    'content': 'Test Content',
                    'created_at': str(post.created_at),
                    'author_id': post.author.id,
                }
            }
        )
