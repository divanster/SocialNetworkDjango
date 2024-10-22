import unittest
from unittest.mock import patch, MagicMock
import json
import time
from newsfeed.consumer import NewsfeedKafkaConsumerClient


class TestNewsfeedKafkaConsumerClient(unittest.TestCase):

    @patch('newsfeed.consumer.KafkaConsumer')
    @patch('newsfeed.consumer.logger')
    def test_kafka_connection_success(self, mock_logger, mock_kafka_consumer):
        """
        Test that the Kafka consumer can successfully connect to a Kafka topic.
        """
        topic = 'NEWSFEED_EVENTS'
        mock_kafka_consumer.return_value = MagicMock()

        consumer_client = NewsfeedKafkaConsumerClient(topic)

        # Check if consumer connects successfully
        self.assertEqual(consumer_client.consumer, mock_kafka_consumer.return_value)
        mock_logger.info.assert_called_with(f"Connected to Kafka topic: {topic}")

    @patch('newsfeed.consumer.KafkaConsumer')
    @patch('newsfeed.consumer.logger')
    @patch('time.sleep', return_value=None)  # To prevent the test from actually sleeping
    def test_kafka_connection_failure(self, mock_sleep, mock_logger, mock_kafka_consumer):
        """
        Test that the Kafka consumer handles a failure to connect correctly.
        """
        # Simulate connection failure
        mock_kafka_consumer.side_effect = Exception("Failed to connect to Kafka")
        topic = 'NEWSFEED_EVENTS'

        with self.assertRaises(RuntimeError):  # Expect RuntimeError due to max retries being exceeded
            NewsfeedKafkaConsumerClient(topic)

        # Verify error message is logged when connection fails
        self.assertGreaterEqual(mock_logger.error.call_count, 1)
        mock_logger.error.assert_any_call(
            "Failed to connect to Kafka: Failed to connect to Kafka. Retrying in 5 seconds..."
        )

    @patch('newsfeed.consumer.KafkaConsumer')
    @patch('newsfeed.consumer.logger')
    def test_consume_messages(self, mock_logger, mock_kafka_consumer):
        """
        Test that the Kafka consumer properly consumes messages from the topic.
        """
        topic = 'NEWSFEED_EVENTS'
        mock_message = MagicMock()
        mock_message.value = json.dumps({'content': 'Test content'})
        mock_kafka_consumer.return_value.__iter__.return_value = [mock_message]

        consumer_client = NewsfeedKafkaConsumerClient(topic)
        messages = list(consumer_client.consume_messages())

        # Ensure the message content is what we expect
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], json.loads(mock_message.value))

        # Ensure that messages are logged properly
        mock_logger.info.assert_called_with(f"Received message: {mock_message.value}")


if __name__ == '__main__':
    unittest.main()
