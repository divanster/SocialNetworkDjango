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

logger = logging.getLogger(__name__)


class AlbumKafkaConsumerClient:
    def __init__(self):
        self.topic = settings.KAFKA_TOPICS.get('ALBUM_EVENTS', 'default-album-topic')
        self.consumer = self.get_kafka_consumer()

    def get_kafka_consumer(self):
        while True:
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
                logger.error(
                    f"[KAFKA] Failed to connect: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def consume_messages(self):
        for message in self.consumer:
            try:
                data = message.value
                # Add custom logic to handle the album event
                logger.info(f"[KAFKA] Received album event: {data}")
                # Handle album events here (e.g., analytics, notifications)
            except Exception as e:
                logger.error(f"[KAFKA] Error processing message: {e}")


def main():
    consumer_client = AlbumKafkaConsumerClient()
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
