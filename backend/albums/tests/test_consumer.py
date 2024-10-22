from unittest import TestCase, mock
from albums.consumer import AlbumKafkaConsumerClient


class TestAlbumKafkaConsumerClient(TestCase):

    @mock.patch('albums.consumer.KafkaConsumer')
    @mock.patch('albums.consumer.Album.objects.using')
    def test_consume_messages(self, mock_using, mock_kafka_consumer):
        # Mock the Kafka message
        mock_message = mock.Mock()
        mock_message.value = {
            'event': 'created',
            'album': 'some_album_id'
        }
        mock_kafka_consumer.return_value.__iter__.return_value = [mock_message]

        # Mock Album retrieval
        mock_album = mock.Mock()
        mock_using.return_value.get.return_value = mock_album

        # Instantiate the consumer and run the test method
        consumer_client = AlbumKafkaConsumerClient()
        consumer_client.consume_messages()

        # Assert that the album was fetched
        mock_using.return_value.get.assert_called_with(pk='some_album_id')
