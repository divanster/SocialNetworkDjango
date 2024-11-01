# backend/kafka_app/base_consumer.py

import os
import time
import logging
import json
import django
from kafka.errors import KafkaError, NoBrokersAvailable, KafkaTimeoutError
from kafka import KafkaConsumer
from django.conf import settings
from django.db import close_old_connections

# Setting up the logger for the consumer
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
            if not os.getenv('DJANGO_SETTINGS_MODULE'):
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
        wait_time = 5  # Seconds to wait between retries

        while retries < max_retries or max_retries == -1:
            try:
                consumer = KafkaConsumer(
                    *self.topics,
                    bootstrap_servers=settings.KAFKA_BROKER_URL,
                    group_id=self.group_id,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                    session_timeout_ms=60000,
                    heartbeat_interval_ms=10000,
                    max_poll_interval_ms=300000
                )
                logger.info(f"Connected to Kafka topics: {', '.join(self.topics)}")
                return consumer
            except (NoBrokersAvailable, KafkaTimeoutError, KafkaError) as e:
                logger.error(
                    f"Failed to connect to Kafka: {e}. Retrying in {wait_time} seconds... ({retries}/{max_retries})"
                )
                retries += 1
                time.sleep(wait_time)

        logger.error("Max retries exceeded. Could not connect to Kafka.")
        raise RuntimeError("Unable to connect to Kafka broker.")

    def consume_messages(self):
        while True:
            try:
                logger.info(
                    f"Started consuming messages from topics: {', '.join(self.topics)}")
                for message in self.consumer:
                    close_old_connections()

                    if not message.value:
                        logger.warning(
                            f"Received an empty message from topic {message.topic}, skipping.")
                        continue

                    try:
                        logger.info(f"Received message: {message.value}")
                        message_data = json.loads(message.value)
                        self.process_message(message_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode JSON message: {e}")
                    except Exception as e:
                        logger.error(f"Failed to process message {message.value}: {e}",
                                     exc_info=True)

            except KafkaError as e:
                logger.error(f"Kafka consumer error: {e}. Retrying in 10 seconds...",
                             exc_info=True)
                time.sleep(10)
            finally:
                self.close()

    def process_message(self, message):
        """
        Placeholder for processing messages. Must be implemented by subclasses.

        Args:
            message (dict): The message to process.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def close(self):
        """
        Close the Kafka consumer.
        """
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            try:
                self.consumer.close()
                logger.info("Kafka consumer closed.")
            except KafkaError as e:
                logger.error(f"Error occurred while closing the Kafka consumer: {e}",
                             exc_info=True)
