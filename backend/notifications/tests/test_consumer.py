import unittest
from unittest.mock import patch, MagicMock
import json
from notifications.consumer import NotificationsKafkaConsumer


class TestNotificationsKafkaConsumer(unittest.TestCase):

    @patch('notifications.consumer.KafkaConsumer')
    @patch('notifications.consumer.logger')
    def test_kafka_connection_success(self, mock_logger, mock_kafka_consumer):
        """
        Test successful Kafka connection.
        """
        topic = 'NOTIFICATIONS_EVENTS'
        mock_kafka_consumer.return_value = MagicMock()

        consumer_client = NotificationsKafkaConsumer(topic)

        self.assertEqual(consumer_client.consumer, mock_kafka_consumer.return_value)
        mock_logger.info.assert_called_with(f"Connected to Kafka topic: {topic}")

    @patch('notifications.consumer.KafkaConsumer')
    @patch('notifications.consumer.logger')
    def test_kafka_connection_failure(self, mock_logger, mock_kafka_consumer):
        """
        Test Kafka connection retry mechanism.
        """
        mock_kafka_consumer.side_effect = Exception("Failed to connect to Kafka")
        topic = 'NOTIFICATIONS_EVENTS'

        with self.assertRaises(Exception):
            NotificationsKafkaConsumer(topic)

        mock_logger.error.assert_called_with(
            "Failed to connect to Kafka: Failed to connect to Kafka. Retrying in 5 "
            "seconds..."
        )

    @patch('notifications.consumer.KafkaConsumer')
    @patch('notifications.consumer.logger')
    def test_consume_messages(self, mock_logger, mock_kafka_consumer):
        """
        Test Kafka message consumption.
        """
        topic = 'NOTIFICATIONS_EVENTS'
        mock_message = MagicMock()
        mock_message.value = json.dumps({'notification': 'Test Notification'})
        mock_kafka_consumer.return_value.__iter__.return_value = [mock_message]

        consumer_client = NotificationsKafkaConsumer(topic)
        consumer_client.consume_messages()

        # Ensure logger logs the consumed message correctly
        mock_logger.info.assert_called_with(
            f"Consumed notification message: {mock_message.value}"
        )


if __name__ == '__main__':
    unittest.main()