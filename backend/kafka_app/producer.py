# kafka_app/producer.py
from kafka import KafkaProducer  # Importing the KafkaProducer
from kafka.errors import KafkaError  # Correct import for KafkaError
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class KafkaProducerClient:
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[settings.KAFKA_BROKER_URL],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("KafkaProducer initialized successfully.")
        except KafkaError as e:
            logger.error(f"Failed to initialize KafkaProducer: {e}")
            raise e

    def send_message(self, topic_key, value):
        topic = settings.KAFKA_TOPICS.get(topic_key)
        if not topic:
            logger.error(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")
            raise ValueError(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")

        try:
            self.producer.send(topic, value=value)
            self.producer.flush()
            logger.info(f"Message sent to topic '{topic_key}': {value}")
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka topic '{topic_key}': {e}")
            raise e

    def close(self):
        if self.producer:
            self.producer.close()
            logger.info("KafkaProducer connection closed.")
