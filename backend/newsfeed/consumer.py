import os
import django
import time
import logging
import json
import sys
from kafka import KafkaConsumer
from django.conf import settings
from newsfeed.services import process_newsfeed_event

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)


class NewsfeedKafkaConsumer:
    def __init__(self):
        self.topic = settings.NEWSFEED_TOPIC
        self.consumer = self.get_kafka_consumer()

    def get_kafka_consumer(self):
        retries = 0
        max_retries = getattr(settings, 'KAFKA_MAX_RETRIES', 5)
        while retries < max_retries or max_retries == -1:
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
                retries += 1
                time.sleep(5)

        logger.error("Max retries exceeded. Could not connect to Kafka.")
        sys.exit(1)

    def consume_messages(self):
        try:
            for message in self.consumer:
                logger.info(f"Received message: {message.value}")
                self.process_event(message.value)
        except Exception as e:
            logger.error(f"Error while consuming messages: {e}")
        finally:
            self.close()

    def process_event(self, message):
        event_type = message.get('event_type')

        # Handle different event types for newsfeed
        if event_type == 'post_created':
            process_newsfeed_event(message['data'])
        elif event_type == 'comment_posted':
            process_newsfeed_event(message['data'])
        elif event_type == 'reaction_added':
            process_newsfeed_event(message['data'])
        # Add more event types if needed

    def close(self):
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("Kafka consumer closed.")


if __name__ == "__main__":
    consumer = NewsfeedKafkaConsumer()
    consumer.consume_messages()
