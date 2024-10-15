import unittest
from unittest.mock import patch, MagicMock, call
from social.consumer import KafkaPostConsumer
import json
import time


class KafkaPostConsumerTestCase(unittest.TestCase):

    @patch('social.consumer.KafkaConsumer')
    def setUp(self, MockKafkaConsumer):
        # Set up a mock KafkaConsumer to use in tests
        self.topic = 'test-topic'
        self.mock_consumer = MockKafkaConsumer.return_value
        self.consumer_client = KafkaPostConsumer(self.topic)

    @patch('social.consumer.KafkaConsumer')
    def test_get_kafka_consumer_success(self, MockKafkaConsumer):
        # Test KafkaConsumer initialization without errors
        MockKafkaConsumer.return_value = self.mock_consumer
        consumer = self.consumer_client.get_kafka_consumer()
        self.assertEqual(consumer, self.mock_consumer)
        self.mock_consumer.__iter__.assert_not_called()  # No consumption yet

    @patch('social.consumer.KafkaConsumer')
    @patch('social.consumer.logger')
    def test_get_kafka_consumer_retry_on_failure(self, mock_logger, MockKafkaConsumer):
        # Simulate KafkaConsumer failure to ensure retry mechanism works
        MockKafkaConsumer.side_effect = [Exception("Kafka connection failed"),
                                         self.mock_consumer]

        consumer = self.consumer_client.get_kafka_consumer()

        self.assertEqual(consumer, self.mock_consumer)
        self.assertEqual(MockKafkaConsumer.call_count, 2)
        mock_logger.error.assert_any_call(
            "Failed to connect to Kafka: Kafka connection failed. Retrying in 5 "
            "seconds...")

    @patch('social.consumer.time.sleep',
           return_value=None)  # Mock time.sleep for faster tests
    def test_consume_messages(self, _):
        # Simulate Kafka message consumption
        mock_message = MagicMock()
        mock_message.value = json.dumps({
            'event': 'created',
            'post_id': '123',
            'title': 'New post title',
            'content': 'This is a test post content'
        }).encode('utf-8')

        self.mock_consumer.__iter__.return_value = [mock_message]

        with patch.object(self.consumer_client,
                          'process_post_event') as mock_process_post_event:
            self.consumer_client.consume_messages()

            # Ensure that the `process_post_event` function is called with decoded
            # JSON data
            mock_process_post_event.assert_called_once_with(
                json.loads(mock_message.value))

    def test_process_post_event_created(self):
        # Test handling of "created" event type
        message = {
            'event': 'created',
            'post_id': '123',
            'title': 'New post title'
        }
        with patch.object(self.consumer_client,
                          'handle_created_post') as mock_handle_created_post:
            self.consumer_client.process_post_event(message)
            mock_handle_created_post.assert_called_once_with(message)

    def test_process_post_event_updated(self):
        # Test handling of "updated" event type
        message = {
            'event': 'updated',
            'post_id': '123',
            'title': 'Updated post title'
        }
        with patch.object(self.consumer_client,
                          'handle_updated_post') as mock_handle_updated_post:
            self.consumer_client.process_post_event(message)
            mock_handle_updated_post.assert_called_once_with(message)

    def test_process_post_event_deleted(self):
        # Test handling of "deleted" event type
        message = {
            'event': 'deleted',
            'post_id': '123'
        }
        with patch.object(self.consumer_client,
                          'handle_deleted_post') as mock_handle_deleted_post:
            self.consumer_client.process_post_event(message)
            mock_handle_deleted_post.assert_called_once_with(message)

    @patch('social.consumer.logger')
    def test_process_post_event_invalid_event(self, mock_logger):
        # Test handling of invalid event type
        message = {
            'event': 'unknown',
            'post_id': '123'
        }
        self.consumer_client.process_post_event(message)
        mock_logger.warning.assert_called_once_with(
            "Unknown event type received: unknown")

    @patch('social.consumer.logger')
    def test_process_post_event_missing_key(self, mock_logger):
        # Test handling of missing event keys
        message = {
            'post_id': '123'
        }
        self.consumer_client.process_post_event(message)
        mock_logger.error.assert_called_once_with(
            "Missing required key in Kafka message: 'event'")

    def test_handle_created_post(self):
        # Test handle_created_post function
        message = {
            'event': 'created',
            'post_id': '123',
            'title': 'Test Post',
            'content': 'This is a test post content'
        }
        with patch('social.consumer.logger') as mock_logger:
            self.consumer_client.handle_created_post(message)
            mock_logger.info.assert_called_once_with(
                f"Handling post creation event: {message}")

    def test_handle_updated_post(self):
        # Test handle_updated_post function
        message = {
            'event': 'updated',
            'post_id': '123',
            'title': 'Updated Title'
        }
        with patch('social.consumer.logger') as mock_logger:
            self.consumer_client.handle_updated_post(message)
            mock_logger.info.assert_called_once_with(
                f"Handling post update event: {message}")

    def test_handle_deleted_post(self):
        # Test handle_deleted_post function
        message = {
            'event': 'deleted',
            'post_id': '123'
        }
        with patch('social.consumer.logger') as mock_logger:
            self.consumer_client.handle_deleted_post(message)
            mock_logger.info.assert_called_once_with(
                f"Handling post deletion event: {message}")


if __name__ == "__main__":
    unittest.main()
