# backend/notifications/consumer.py

import os
import django
import time
import json
import logging
from kafka import KafkaConsumer
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)


class NotificationsKafkaConsumer:
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
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                logger.info(f"Connected to Kafka topic: {self.topic}")
                return consumer
            except Exception as e:
                logger.error(
                    f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def consume_messages(self):
        for message in self.consumer:
            try:
                # Process the notification message
                logger.info(f"Consumed notification message: {message.value}")
                # Add your processing logic here
            except Exception as e:
                logger.error(f"Error processing message: {e}")


# To run this consumer, you can create a separate script or call it directly:
if __name__ == "__main__":
    consumer_client = NotificationsKafkaConsumer('NOTIFICATIONS_EVENTS')
    consumer_client.consume_messages()
