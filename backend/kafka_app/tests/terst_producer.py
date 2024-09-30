# kafka_app/tests/test_producer.py
from django.test import TestCase
from unittest.mock import patch
from kafka_app.producer import KafkaProducerClient


class KafkaProducerClientTestCase(TestCase):
    @patch('kafka.KafkaProducer')
    def test_send_message(self, MockKafkaProducer):
        mock_producer_instance = MockKafkaProducer.return_value
        producer_client = KafkaProducerClient()

        producer_client.send_message('USER_EVENTS', {"key": "value"})

        mock_producer_instance.send.assert_called_with('user-events',
                                                       value=b'{"key": "value"}')
        mock_producer_instance.flush.assert_called_once()
