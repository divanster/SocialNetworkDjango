from django.test import TestCase
from unittest.mock import patch
from social.models import Post
from django.contrib.auth import get_user_model
from newsfeed.tasks import send_newsfeed_event_to_kafka
from newsfeed.tasks import logger  # Assuming logger is being used in your task

User = get_user_model()


class TestNewsfeedTasks(TestCase):

    def setUp(self):
        # Create a user to be used in the tests
        self.user = User.objects.create_user(username='testuser',
                                             email='test@example.com',
                                             password='password')

    @patch('newsfeed.tasks.KafkaProducerClient.send_message')
    def test_send_newsfeed_event_to_kafka(self, mock_send_message):
        # Create a post instance
        post = Post.objects.create(author=self.user, title='Test Post',
                                   content='Test Content')

        # Call the task function to trigger sending the message
        send_newsfeed_event_to_kafka(post.id, 'created', 'Post')

        # Verify that send_message was called with the correct arguments
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

    @patch('newsfeed.tasks.KafkaProducerClient.send_message')
    @patch('newsfeed.tasks.logger')
    def test_send_newsfeed_event_to_kafka_object_does_not_exist(self, mock_logger,
                                                                mock_send_message):
        # Attempt to call the task with a non-existing post ID
        non_existing_id = 9999
        send_newsfeed_event_to_kafka(non_existing_id, 'created', 'Post')

        # Verify that send_message was not called
        mock_send_message.assert_not_called()

        # Ensure logger.error was called with the correct message
        mock_logger.error.assert_called_once_with(
            f"Post with ID {non_existing_id} does not exist.")

    @patch('newsfeed.tasks.KafkaProducerClient.send_message')
    @patch('newsfeed.tasks.logger')
    def test_send_newsfeed_event_to_kafka_handle_general_exception(self, mock_logger,
                                                                   mock_send_message):
        # Create a post instance
        post = Post.objects.create(author=self.user, title='Test Post',
                                   content='Test Content')

        # Simulate an exception when trying to send a message
        mock_send_message.side_effect = Exception("Kafka send error")

        # Call the task function to trigger sending the message
        send_newsfeed_event_to_kafka(post.id, 'created', 'Post')

        # Verify that logger.error was called with the correct message
        mock_logger.error.assert_called_once_with(
            "Error sending Kafka message: Kafka send error")
