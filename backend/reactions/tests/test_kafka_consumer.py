import pytest
from unittest import mock
from kafka import KafkaConsumer
from reactions.consumer import KafkaReactionConsumer
import logging

logger = logging.getLogger(__name__)


@mock.patch('kafka.KafkaConsumer')
def test_kafka_reaction_consumer_initialize(mock_kafka_consumer):
    topic = "REACTION_EVENTS"
    consumer = KafkaReactionConsumer(topic)

    # Check if KafkaConsumer was called with the correct parameters
    mock_kafka_consumer.assert_called_with(
        topic,
        bootstrap_servers=mock.ANY,
        group_id=mock.ANY,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=mock.ANY
    )


@mock.patch.object(KafkaConsumer, '__next__', return_value=mock.Mock(
    value='{"reaction_id": 1, "action": "created"}'))
@mock.patch('kafka.KafkaConsumer')
def test_kafka_reaction_consumer_consume_message(mock_kafka_consumer, mock_next):
    topic = "REACTION_EVENTS"
    consumer = KafkaReactionConsumer(topic)
    messages = consumer.consume_messages()

    message = next(messages)
    assert message == '{"reaction_id": 1, "action": "created"}'
