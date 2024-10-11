# backend/tagging/consumer.py

import os
import django
import time
import logging
from kafka import KafkaConsumer
from django.conf import settings
from .models import TaggedItem
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)


class KafkaTaggingConsumer:
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
                logger.error(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def consume_messages(self):
        for message in self.consumer:
            try:
                self.process_message(message.value)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    def process_message(self, message):
        # Process the tagging event
        event_type = message.get('event')
        tagged_item_id = message.get('tagged_item_id')

        if event_type == 'created':
            logger.info(f"Processing 'created' tagging event for TaggedItem ID: {tagged_item_id}")
            # Here you can add additional logic to process the creation of tags
        elif event_type == 'deleted':
            logger.info(f"Processing 'deleted' tagging event for TaggedItem ID: {tagged_item_id}")
            # Here you can add additional logic to process tag deletion
        else:
            logger.warning(f"Unknown tagging event type: {event_type}")

        logger.info(f"Processed tagging event: {message}")


def main():
    topic = settings.KAFKA_TOPICS.get('TAGGING_EVENTS', 'default-tagging-topic')
    consumer_client = KafkaTaggingConsumer(topic)
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
