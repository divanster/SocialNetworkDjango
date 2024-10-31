# backend/kafka_app/base_consumer.py

import os
import time
import logging
import json
import django
from kafka.errors import KafkaError
from kafka import KafkaConsumer
from django.conf import settings
from django.db import close_old_connections

logger = logging.getLogger(__name__)

class BaseKafkaConsumer:
    def __init__(self, topics, group_id):
        """
        Initialize the Base Kafka Consumer with topic and group ID.
        Args:
            topics (list[str]): List of topics to subscribe to.
            group_id (str): Kafka consumer group ID.
        """
        self.setup_django()
        self.topics = topics if isinstance(topics, list) else [topics]
        self.group_id = group_id
        self.consumer = self.get_kafka_consumer()

    @staticmethod
    def setup_django():
        """
        Set up the Django environment. Required to access Django services and models.
        """
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            django.setup()
            logger.info("Django setup completed successfully.")
        except Exception as e:
            logger.error(f"Failed to set up Django: {e}")
            raise e

    def get_kafka_consumer(self):
        """
        Initialize the Kafka Consumer.
        Retries up to max_retries times before raising an exception.
        """
        retries = 0
        max_retries = getattr(settings, 'KAFKA_MAX_RETRIES', 5)

        while retries < max_retries or max_retries == -1:
            try:
                consumer = KafkaConsumer(
                    *self.topics,
                    bootstrap_servers=settings.KAFKA_BROKER_URL,
                    group_id=self.group_id,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                logger.info(f"Connected to Kafka topics: {', '.join(self.topics)}")
                return consumer
            except KafkaError as e:
                logger.error(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
                retries += 1
                time.sleep(5)

        logger.error("Max retries exceeded. Could not connect to Kafka.")
        raise RuntimeError("Unable to connect to Kafka broker.")

    def consume_messages(self):
        """
        Consume messages from Kafka topics.
        """
        try:
            logger.info(f"Starting to consume messages from topics: {', '.join(self.topics)}")
            for message in self.consumer:
                # Close old DB connections to prevent issues with long-running consumers
                close_old_connections()

                logger.info(f"Received message from topic {message.topic}: {message.value}")
                try:
                    self.process_message(message.value)
                except Exception as e:
                    logger.error(f"Failed to process message: {e}", exc_info=True)
        except KafkaError as e:
            logger.error(f"Kafka consumer error: {e}", exc_info=True)
        finally:
            self.close()

    def process_message(self, message):
        """
        Placeholder for processing messages. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def close(self):
        """
        Close the Kafka consumer.
        """
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("Kafka consumer closed.")
