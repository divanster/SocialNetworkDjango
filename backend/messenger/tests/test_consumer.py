import unittest
from unittest.mock import patch, MagicMock
import json
import logging
from messenger.consumer import MessengerKafkaConsumerClient


class TestMessengerKafkaConsumerClient(unittest.TestCase):
    def setUp(self):
        self.topic = 'MESSENGER_EVENTS'
        self.consumer_client = MessengerKafkaConsumerClient(self.topic)
        self.mock_consumer = MagicMock()

    @patch('messenger.consumer.KafkaConsumer')
    @patch('messenger.consumer.logger')
    def test_kafka_connection_success(self, mock_logger, mock_kafka_consumer):
        # Simulate successful connection to Kafka
        mock_kafka_consumer.return_value = self.mock_consumer
        consumer = self.consumer_client.get_kafka_consumer()

        # Check that a KafkaConsumer was created and connected
        mock_kafka_consumer.assert_called_once_with(
            self.topic,
            bootstrap_servers='localhost:9092',
            group_id='default_group',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: x.decode('utf-8')
        )
        self.assertEqual(consumer, self.mock_consumer)
        mock_logger.info.assert_called_once_with(
            f"Connected to Kafka topic: {self.topic}")

    @patch('messenger.consumer.KafkaConsumer')
    @patch('messenger.consumer.logger')
    def test_kafka_connection_failure(self, mock_logger, mock_kafka_consumer):
        # Simulate a failure in connecting to Kafka
        mock_kafka_consumer.side_effect = Exception("Kafka connection failed")

        with self.assertRaises(Exception):
            self.consumer_client.get_kafka_consumer()

        # Verify that the error is logged
        mock_logger.error.assert_called_with(
            "Failed to connect to Kafka: Kafka connection failed. Retrying in 5 "
            "seconds..."
        )

    @patch('messenger.consumer.KafkaConsumer')
    @patch('messenger.consumer.logger')
    def test_consume_messages(self, mock_logger, mock_kafka_consumer):
        # Simulate Kafka messages being consumed
        mock_kafka_consumer.return_value = self.mock_consumer

        # Create a mock Kafka message
        mock_message = MagicMock()
        mock_message.value = json.dumps(
            {"message_id": "123", "content": "Hello, World!"})
        self.mock_consumer.__iter__.return_value = [mock_message]

        # Call consume_messages and capture the generator output
        messages = list(self.consumer_client.consume_messages())

        # Verify that the consumer received and yielded the correct messages
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], json.loads(mock_message.value))

        # Check that the logger logged the received message
        mock_logger.info.assert_called_with(f"Received message: {mock_message.value}")


if __name__ == '__main__':
    unittest.main()
