# backend/follows/consumer.py
import os
import django
import time
import logging
from kafka import KafkaConsumer
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)


class KafkaConsumerClient:
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
                logger.error(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def consume_messages(self):
        for message in self.consumer:
            logger.info(f"Received message: {message.value}")
            self.process_message(message.value)

    def process_message(self, message):
        # Add your custom processing logic here if needed
        logger.info(f"Processing message: {message}")


def main():
    topic = settings.KAFKA_TOPICS.get('FOLLOW_EVENTS', 'default-follow-topic')
    consumer_client = KafkaConsumerClient(topic)
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
