from django.test import TestCase
from unittest.mock import patch, MagicMock
from social.models import Post
from django.contrib.auth import get_user_model
from kafka_app.producer import KafkaProducerClient
from social.tasks import send_post_event_to_kafka, consume_post_events
from celery import shared_task
from django.conf import settings
import json

User = get_user_model()


class SendPostEventToKafkaTest(TestCase):

    def setUp(self):
        # Create a user and a post for testing purposes
        self.user = User.objects.create_user(
            username='author', email='author@example.com', password='password123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author_id=self.user.id,
            author_username=self.user.username,
        )
        self.kafka_topic = settings.KAFKA_TOPICS.get('POST_EVENTS',
                                                     'default-post-topic')

    @patch.object(KafkaProducerClient, 'send_message')
    def test_send_post_created_event_to_kafka(self, mock_send_message):
        # Mock the Kafka producer client to avoid sending real Kafka messages
        send_post_event_to_kafka(self.post.id, 'created')

        # Assert KafkaProducerClient.send_message() was called with the correct
        # arguments
        mock_send_message.assert_called_once()
        args, kwargs = mock_send_message.call_args
        topic, message = args
        self.assertEqual(topic, self.kafka_topic)
        self.assertEqual(message['post_id'], str(self.post.id))
        self.assertEqual(message['event'], 'created')
        self.assertEqual(message['title'], self.post.title)
        self.assertEqual(message['content'], self.post.content)

    @patch.object(KafkaProducerClient, 'send_message')
    def test_send_post_updated_event_to_kafka(self, mock_send_message):
        # Update post details and send updated event to Kafka
        self.post.title = "Updated Post"
        self.post.save()

        send_post_event_to_kafka(self.post.id, 'updated')

        # Assert that send_message was called for the updated event
        mock_send_message.assert_called_once()
        args, kwargs = mock_send_message.call_args
        topic, message = args
        self.assertEqual(topic, self.kafka_topic)
        self.assertEqual(message['post_id'], str(self.post.id))
        self.assertEqual(message['event'], 'updated')
        self.assertEqual(message['title'], self.post.title)

    @patch.object(KafkaProducerClient, 'send_message')
    def test_send_post_deleted_event_to_kafka(self, mock_send_message):
        # Delete post and send deleted event to Kafka
        send_post_event_to_kafka(self.post.id, 'deleted')

        # Assert that send_message was called for the deleted event
        mock_send_message.assert_called_once()
        args, kwargs = mock_send_message.call_args
        topic, message = args
        self.assertEqual(topic, self.kafka_topic)
        self.assertEqual(message['post_id'], str(self.post.id))
        self.assertEqual(message['action'], 'deleted')

    @patch('social.tasks.logger.error')
    @patch.object(KafkaProducerClient, 'send_message',
                  side_effect=Exception("Kafka connection failed"))
    def test_send_post_event_to_kafka_with_error(self, mock_send_message,
                                                 mock_logger_error):
        # Trigger an exception to test error handling in send_post_event_to_kafka
        send_post_event_to_kafka(self.post.id, 'created')

        # Assert the logger's error method was called due to an exception
        mock_logger_error.assert_called_with(
            "Error sending Kafka message: Kafka connection failed")


class ConsumePostEventsTest(TestCase):

    @patch('social.tasks.KafkaConsumerClient')
    @patch('social.tasks.logger')
    def test_consume_post_events_created(self, mock_logger, mock_kafka_consumer):
        # Setup mock for KafkaConsumerClient to simulate a Kafka message
        mock_consumer_instance = MagicMock()
        mock_consumer_instance.consume_messages.return_value = [
            json.dumps({
                'event': 'created',
                'post_id': '12345',
                'title': 'Test Post',
                'content': 'Test content'
            })
        ]
        mock_kafka_consumer.return_value = mock_consumer_instance

        # Call the consume_post_events task
        consume_post_events()

        # Assert that logger was called with correct log messages
        mock_logger.info.assert_any_call(
            "Processing created post event for post ID: 12345")

    @patch('social.tasks.KafkaConsumerClient')
    @patch('social.tasks.logger')
    def test_consume_post_events_updated(self, mock_logger, mock_kafka_consumer):
        # Setup mock for KafkaConsumerClient to simulate an update event
        mock_consumer_instance = MagicMock()
        mock_consumer_instance.consume_messages.return_value = [
            json.dumps({
                'event': 'updated',
                'post_id': '12345',
                'title': 'Updated Test Post',
                'content': 'Updated content'
            })
        ]
        mock_kafka_consumer.return_value = mock_consumer_instance

        # Call the consume_post_events task
        consume_post_events()

        # Assert that logger was called for the updated event
        mock_logger.info.assert_any_call(
            "Processing updated post event for post ID: 12345")

    @patch('social.tasks.KafkaConsumerClient')
    @patch('social.tasks.logger')
    def test_consume_post_events_deleted(self, mock_logger, mock_kafka_consumer):
        # Setup mock for KafkaConsumerClient to simulate a delete event
        mock_consumer_instance = MagicMock()
        mock_consumer_instance.consume_messages.return_value = [
            json.dumps({
                'event': 'deleted',
                'post_id': '12345'
            })
        ]
        mock_kafka_consumer.return_value = mock_consumer_instance

        # Call the consume_post_events task
        consume_post_events()

        # Assert that logger was called for the deleted event
        mock_logger.info.assert_any_call(
            "Processing deleted post event for post ID: 12345")

    @patch('social.tasks.KafkaConsumerClient')
    @patch('social.tasks.logger')
    def test_consume_post_events_invalid_event(self, mock_logger, mock_kafka_consumer):
        # Setup mock to simulate an invalid event type
        mock_consumer_instance = MagicMock()
        mock_consumer_instance.consume_messages.return_value = [
            json.dumps({
                'event': 'invalid_event',
                'post_id': '12345'
            })
        ]
        mock_kafka_consumer.return_value = mock_consumer_instance

        # Call the consume_post_events task
        consume_post_events()

        # Assert that logger was called with a warning for an unknown event type
        mock_logger.warning.assert_called_with(
            "Unknown post event type received: invalid_event")

    @patch('social.tasks.KafkaConsumerClient')
    @patch('social.tasks.logger')
    def test_consume_post_events_missing_key(self, mock_logger, mock_kafka_consumer):
        # Setup mock to simulate a Kafka message missing the 'event' key
        mock_consumer_instance = MagicMock()
        mock_consumer_instance.consume_messages.return_value = [
            json.dumps({
                'post_id': '12345'
            })
        ]
        mock_kafka_consumer.return_value = mock_consumer_instance

        # Call the consume_post_events task
        consume_post_events()

        # Assert that logger was called for missing key
        mock_logger.error.assert_called_with(
            "Missing key in post event message: 'event'")

