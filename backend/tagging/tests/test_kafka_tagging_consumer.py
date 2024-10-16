# tagging/tests/test_kafka_tagging_consumer.py
import pytest
from unittest.mock import patch, MagicMock
from tagging.consumer import KafkaTaggingConsumer


@pytest.fixture
def kafka_consumer():
    return KafkaTaggingConsumer(topic='test-topic')


@patch('tagging.consumer.KafkaConsumer')
def test_get_kafka_consumer_success(mock_kafka_consumer, kafka_consumer):
    # Mocking KafkaConsumer to prevent an actual connection
    kafka_consumer.get_kafka_consumer()
    mock_kafka_consumer.assert_called_once()


@patch('tagging.consumer.KafkaTaggingConsumer.process_message')
def test_consume_messages(mock_process_message, kafka_consumer):
    mock_message = MagicMock()
    mock_message.value = {'event': 'created', 'tagged_item_id': 1}
    kafka_consumer.consumer = [mock_message]

    kafka_consumer.consume_messages()
    mock_process_message.assert_called_with(mock_message.value)


def test_process_message_created_event(kafka_consumer):
    with patch('logging.Logger.info') as mock_logger_info:
        kafka_consumer.process_message({'event': 'created', 'tagged_item_id': 1})
        mock_logger_info.assert_called_with(
            "Processing 'created' tagging event for TaggedItem ID: 1")
