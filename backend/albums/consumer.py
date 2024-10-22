# backend/albums/consumer.py
import os
import django
import time
import logging
from kafka import KafkaConsumer
from django.conf import settings
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from albums.models import Album

logger = logging.getLogger(__name__)


class AlbumKafkaConsumerClient:
    def __init__(self):
        self.topic = settings.KAFKA_TOPICS.get('ALBUM_EVENTS', 'default-album-topic')
        self.consumer = self.get_kafka_consumer()

    def get_kafka_consumer(self):
        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=settings.KAFKA_BROKER_URL,
                    group_id=settings.KAFKA_CONSUMER_GROUP_ID,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                logger.info(f"[KAFKA] Connected to topic: {self.topic}")
                return consumer
            except Exception as e:
                retry_count += 1
                wait_time = min(5 * (2 ** retry_count),
                                60)  # Exponential backoff with max wait of 60 seconds
                logger.error(
                    f"[KAFKA] Failed to connect (attempt {retry_count}): {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        raise ConnectionError("[KAFKA] Max retries reached. Could not connect to "
                              "Kafka broker.")

    def consume_messages(self):
        for message in self.consumer:
            try:
                data = message.value
                logger.info(f"[KAFKA] Received album event: {data}")
                self.handle_album_event(data)
            except Exception as e:
                logger.error(f"[KAFKA] Error processing message: {e}")

    def handle_album_event(self, data):
        # Handle logic for MongoDB data if needed
        event_type = data.get('event')
        if event_type == 'created':
            album_id = data.get('album')
            try:
                album = Album.objects.using('social_db').get(pk=album_id)
                logger.info(f"[KAFKA] Successfully fetched album: {album}")
            except Album.DoesNotExist:
                logger.error(f"[KAFKA] Album with ID {album_id} does not exist.")


def main():
    consumer_client = AlbumKafkaConsumerClient()
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
