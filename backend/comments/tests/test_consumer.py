# backend/comments/tests/test_consumer.py

import unittest
from unittest.mock import patch, MagicMock, call
from comments.consumer import KafkaConsumerClient
from django.conf import settings
import logging

# Setting up the logger
logger = logging.getLogger(__name__)


class TestKafkaConsumerClient(unittest.TestCase):
    """
    Unit test case for KafkaConsumerClient, which tests initialization,
    retry mechanism, and message consumption from Kafka.
    """

    @patch('comments.consumer.KafkaConsumer')
    def test_initialization(self, MockKafkaConsumer):
        """
        Test initialization of KafkaConsumerClient.
        - Ensure that the KafkaConsumer is correctly instantiated.
        """
        # Given a Kafka topic
        topic = "test-topic"

        # When we initialize the KafkaConsumerClient
        client = KafkaConsumerClient(topic)

        # Then the topic should be set correctly
        self.assertEqual(client.topic, topic)

        # And the KafkaConsumer should have been called to create a consumer
        MockKafkaConsumer.assert_called_once()

    @patch('comments.consumer.KafkaConsumer',
           side_effect=Exception("Kafka connection failed"))
    @patch('time.sleep', return_value=None)
    def test_kafka_retry_mechanism(self, mock_sleep, MockKafkaConsumer):
        """
        Test retry mechanism in KafkaConsumerClient.
        - Ensure that the Kafka consumer retries connecting when an exception is raised.
        """
        # Given that KafkaConsumer raises an exception (e.g., unable to connect)
        topic = "test-topic"

        # We will patch time.sleep to avoid delays during the test

        # When we initialize the KafkaConsumerClient with retries
        with self.assertLogs(logger, level='ERROR') as log:
            # Expecting an exception since the consumer fails to connect and we simulate retries
            with self.assertRaises(Exception):
                KafkaConsumerClient(topic)

        # The log should show retry attempts for Kafka connection failure
        self.assertTrue(
            any("Failed to connect to Kafka" in message for message in log.output)
        )

    @patch('comments.consumer.KafkaConsumer')
    def test_consume_messages(self, MockKafkaConsumer):
        """
        Test message consumption using KafkaConsumerClient.
        - Ensure that messages can be correctly consumed from the Kafka topic.
        """
        # Given a mocked KafkaConsumer
        topic = "test-topic"
        mock_message = MagicMock()
        mock_message.value = '{"comment": "This is a test comment"}'
        mock_consumer_instance = MockKafkaConsumer.return_value
        mock_consumer_instance.__iter__.return_value = [mock_message]

        # When we initialize the KafkaConsumerClient
        client = KafkaConsumerClient(topic)

        # Then when consume_messages is called, it should yield messages from Kafka
        messages = list(client.consume_messages())

        # Ensure that we receive the correct number of messages
        self.assertEqual(len(messages), 1)

        # Ensure that the message content is as expected
        self.assertEqual(messages[0], '{"comment": "This is a test comment"}')


if __name__ == "__main__":
    unittest.main()
