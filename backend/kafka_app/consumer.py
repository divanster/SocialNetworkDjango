# backend/kafka_app/consumer.py

import os
import django
import time
import logging
import json
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
        retries = 0
        max_retries = getattr(settings, 'KAFKA_MAX_RETRIES', 5)
        wait_time = 5  # seconds

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
                logger.error(f"Failed to connect to Kafka: {e}. Retrying in {wait_time} seconds...")
                retries += 1
                time.sleep(wait_time)

        logger.error("Max retries exceeded. Could not connect to Kafka.")
        raise RuntimeError("KafkaConsumerClient: Unable to connect to Kafka broker.")

    def consume_messages(self):
        try:
            for message in self.consumer:
                # Process the message
                logger.info(f"Received message: {message.value}")
                self.process_message(message.value)
        except Exception as e:
            logger.error(f"Error while consuming messages: {e}")
        finally:
            self.close()

    def process_message(self, message):
        """
        Placeholder function for message processing logic.
        """
        try:
            logger.info(f"Processing message: {message}")
            # Your actual message processing code here
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def close(self):
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("Kafka consumer closed.")

def main():
    topic = settings.KAFKA_TOPICS['ALBUM_EVENTS']
    consumer_client = KafkaConsumerClient(topic)
    consumer_client.consume_messages()

if __name__ == "__main__":
    main()
