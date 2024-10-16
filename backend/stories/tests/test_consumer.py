from unittest import TestCase
from unittest.mock import patch, MagicMock
from stories.consumer import KafkaStoryConsumer


class TestKafkaStoryConsumer(TestCase):

    @patch('stories.consumer.KafkaConsumer')
    @patch('stories.consumer.settings.KAFKA_BROKER_URL', 'localhost:9092')
    @patch('stories.consumer.settings.KAFKA_CONSUMER_GROUP_ID', 'test-group')
    def test_get_kafka_consumer(self, MockKafkaConsumer):
        # Arrange
        topic = 'test-topic'
        consumer = KafkaStoryConsumer(topic)

        # Act
        kafka_consumer = consumer.get_kafka_consumer()

        # Assert
        MockKafkaConsumer.assert_called_once_with(
            topic,
            bootstrap_servers='localhost:9092',
            group_id='test-group',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=MagicMock()
        )
        self.assertIsNotNone(kafka_consumer)

    @patch('stories.consumer.KafkaStoryConsumer.process_message')
    def test_consume_messages(self, mock_process_message):
        topic = 'test-topic'
        consumer = KafkaStoryConsumer(topic)

        # Mocking the Kafka consumer and its iterator
        mock_message = MagicMock()
        mock_message.value = {'event': 'created', 'story_id': 1}
        consumer.consumer = [mock_message]

        consumer.consume_messages()

        # Check if the message is processed correctly
        mock_process_message.assert_called_once_with(
            {'event': 'created', 'story_id': 1})
