import os
import time
import logging
import json
import django
from kafka import KafkaConsumer
from django.conf import settings
from django.db import close_old_connections

logger = logging.getLogger(__name__)


class BaseKafkaConsumer:
    def __init__(self, topic, group_id):
        self.setup_django()  # Setup Django before any processing starts

        self.topic = topic
        self.group_id = group_id
        self.consumer = self.get_kafka_consumer()

    @staticmethod
    def setup_django():
        # Ensure Django is set up properly by configuring settings before anything else
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            django.setup()
            logger.info("Django setup completed successfully.")
        except Exception as e:
            logger.error(f"Failed to set up Django: {e}")
            raise e

    def get_kafka_consumer(self):
        retries = 0
        max_retries = getattr(settings, 'KAFKA_MAX_RETRIES', 5)
        wait_time = 5  # seconds

        while retries < max_retries or max_retries == -1:
            try:
                consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=settings.KAFKA_BROKER_URL,
                    group_id=self.group_id,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                logger.info(f"Connected to Kafka topic: {self.topic}")
                return consumer
            except Exception as e:
                logger.error(
                    f"Failed to connect to Kafka: {e}. Retrying in {wait_time} seconds...")
                retries += 1
                time.sleep(wait_time)

        logger.error("Max retries exceeded. Could not connect to Kafka.")
        raise RuntimeError("Unable to connect to Kafka broker.")

    def consume_messages(self):
        try:
            for message in self.consumer:
                close_old_connections()  # Ensure fresh database connections
                logger.info(
                    f"Received message from topic {message.topic}: {message.value}")
                self.process_message(message.value)
        except Exception as e:
            logger.error(f"Error while consuming messages: {e}")
        finally:
            self.close()

    def process_message(self, message):
        raise NotImplementedError("Subclasses must implement this method.")

    def close(self):
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("Kafka consumer closed.")
