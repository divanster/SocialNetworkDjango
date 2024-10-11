# backend/newsfeed/consumer.py
import os
import django
import logging
import json
import time
from kafka import KafkaConsumer
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)


class NewsfeedKafkaConsumerClient:
    def __init__(self, topic):
        self.topic = topic
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
                    value_deserializer=lambda x: x.decode('utf-8')
                )
                logger.info(f"Connected to Kafka topic: {self.topic}")
                return consumer
            except Exception as e:
                logger.error(
                    f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
                time.sleep(
                    5)  # Using time module here to sleep for 5 seconds before retrying

    def consume_messages(self):
        for message in self.consumer:
            yield json.loads(
                message.value)  # Using json module here to parse the message value
