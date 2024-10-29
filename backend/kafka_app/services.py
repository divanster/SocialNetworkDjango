# backend/kafka_app/services.py

import json
import logging
from kafka import KafkaProducer
from django.conf import settings

logger = logging.getLogger(__name__)


class KafkaService:
    _producer = None

    @classmethod
    def get_producer(cls):
        if cls._producer is None:
            try:
                cls._producer = KafkaProducer(
                    bootstrap_servers=[settings.KAFKA_BROKER_URL],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    retries=5
                )
                logger.info("KafkaProducer initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize KafkaProducer: {e}")
                raise e
        return cls._producer

    @classmethod
    def send_event(cls, topic_key, message):
        try:
            topic = settings.KAFKA_TOPICS.get(topic_key)
            if not topic:
                raise ValueError(
                    f"Topic key '{topic_key}' not found in KAFKA_TOPICS settings.")
            producer = cls.get_producer()
            producer.send(topic, value=message)
            producer.flush()
            logger.info(f"Message sent to topic '{topic}': {message}")
        except Exception as e:
            logger.error(f"Failed to send message to Kafka topic '{topic_key}': {e}")
            raise e
