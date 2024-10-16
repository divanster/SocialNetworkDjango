# tagging/tests/test_tasks.py
import pytest
from unittest.mock import patch, MagicMock
from tagging.tasks import send_tagging_event_to_kafka, consume_tagging_events


@pytest.mark.django_db
@patch('tagging.tasks.KafkaProducerClient.send_message')
def test_send_tagging_event_to_kafka_created(mock_send_message):
    tagged_item = MagicMock()
    tagged_item.id = 1
    tagged_item.tagged_user_id = 1
    send_tagging_event_to_kafka(tagged_item.id, 'created')
    mock_send_message.assert_called_once()


@pytest.mark.django_db
@patch('tagging.tasks.KafkaConsumerClient.consume_messages')
def test_consume_tagging_events(mock_consume_messages):
    mock_consume_messages.return_value = [{'event': 'created', 'tagged_item_id': 1}]
    consume_tagging_events()
    mock_consume_messages.assert_called_once()
