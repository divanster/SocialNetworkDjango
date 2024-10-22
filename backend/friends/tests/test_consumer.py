import unittest
from unittest.mock import patch, MagicMock, call
import time
from friends.consumer import KafkaConsumerClient


class TestKafkaConsumerClient(unittest.TestCase):
    """
    Test case for the KafkaConsumerClient class that handles the connection and message
    consumption from Kafka topics for the Friends app.
    """

    @patch('friends.consumer.KafkaConsumer')
    @patch('friends.consumer.settings')
    @patch('friends.consumer.logger')
    def test_successful_kafka_connection(self, mock_logger, mock_settings, mock_kafka_consumer):
        """
        Test that KafkaConsumerClient successfully connects to Kafka and logs the successful connection.
        """
        # Mock settings for Kafka
        mock_settings.KAFKA_BROKER_URL = 'localhost:9092'
        mock_settings.KAFKA_CONSUMER_GROUP_ID = 'test_group'

        # Instantiate the consumer client
        consumer_client = KafkaConsumerClient('FRIEND_EVENTS')

        # Ensure KafkaConsumer was initialized correctly with expected arguments
        mock_kafka_consumer.assert_called_once_with(
            'FRIEND_EVENTS',
            bootstrap_servers='localhost:9092',
            group_id='test_group',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: x.decode('utf-8')
        )

        # Ensure that a successful connection message is logged
        mock_logger.info.assert_called_with("Connected to Kafka topic: FRIEND_EVENTS")

    @patch('friends.consumer.KafkaConsumer', side_effect=Exception("Kafka connection failed"))
    @patch('friends.consumer.settings')
    @patch('friends.consumer.logger')
    @patch('time.sleep', return_value=None)  # To avoid slowing down tests with sleep
    def test_kafka_connection_retry(self, mock_sleep, mock_logger, mock_settings, mock_kafka_consumer):
        """
        Test that KafkaConsumerClient retries to connect if the initial connection fails.
        """
        # Mock settings for Kafka
        mock_settings.KAFKA_BROKER_URL = 'localhost:9092'
        mock_settings.KAFKA_CONSUMER_GROUP_ID = 'test_group'

        # Instantiate the consumer client and expect retries due to Kafka connection failure
        with self.assertRaises(Exception):  # Eventually raises Exception as no connection can be made
            consumer_client = KafkaConsumerClient('FRIEND_EVENTS')

        # Ensure the retry logic was executed at least twice
        self.assertGreaterEqual(mock_kafka_consumer.call_count, 2)

        # Ensure that the appropriate log message for failed connection was logged
        mock_logger.error.assert_any_call("Failed to connect to Kafka: Kafka connection failed. Retrying in 5 seconds...")

        # Verify that sleep was called to implement retry delay
        mock_sleep.assert_called_with(5)

    @patch('friends.consumer.KafkaConsumer')
    @patch('friends.consumer.settings')
    @patch('friends.consumer.logger')
    def test_message_consumption(self, mock_logger, mock_settings, mock_kafka_consumer):
        """
        Test that KafkaConsumerClient can successfully consume messages and log them.
        """
        # Mock settings for Kafka
        mock_settings.KAFKA_BROKER_URL = 'localhost:9092'
        mock_settings.KAFKA_CONSUMER_GROUP_ID = 'test_group'

        # Mock KafkaConsumer to return a fake message
        mock_message = MagicMock()
        mock_message.value = '{"friendship_id": "1234", "action": "created"}'
        mock_kafka_consumer.return_value = [mock_message]

        # Instantiate the consumer client and consume messages
        consumer_client = KafkaConsumerClient('FRIEND_EVENTS')
        consumer_client.consume_messages()

        # Check that the logger logged the received message correctly
        mock_logger.info.assert_called_with('Received message: {"friendship_id": "1234", "action": "created"}')


if __name__ == '__main__':
    unittest.main()
