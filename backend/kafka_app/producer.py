# backend/kafka_app/producer.py

from kafka import KafkaProducer
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class KafkaProducerClient:
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[settings.KAFKA_BROKER_URL],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=5
            )
            logger.info("KafkaProducer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize KafkaProducer: {e}")
            raise e

    def send_message(self, topic_key, message):
        topic = settings.KAFKA_TOPICS.get(topic_key)
        if not topic:
            logger.error(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")
            raise ValueError(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")
        try:
            self.producer.send(topic, value=message)
            self.producer.flush()
            logger.info(f"Message sent to topic '{topic}': {message}")
        except Exception as e:
            logger.error(f"Failed to send message to topic '{topic}': {e}")
            raise e
