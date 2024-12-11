# backend/kafka_app/producer.py

import json
import logging
from kafka import KafkaProducer
from django.conf import settings
from cryptography.fernet import Fernet
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class EventData(BaseModel):
    user_id: int
    username: str
    event: str

    class Config:
        str_min_length = 1


class KafkaProducerClient:
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[settings.KAFKA_BROKER_URL],
                retries=5  # Removed `value_serializer` here
            )
            self.key = settings.KAFKA_ENCRYPTION_KEY.encode()
            self.cipher_suite = Fernet(self.key)
            logger.info("KafkaProducer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize KafkaProducer: {e}")
            raise e

    def encrypt_message(self, message):
        """Encrypts a message before sending."""
        message_bytes = json.dumps(message).encode(
            'utf-8')  # Convert to JSON and then to bytes
        encrypted_message = self.cipher_suite.encrypt(message_bytes)
        return encrypted_message

    def send(self, topic, value):
        """Send a message to Kafka."""
        try:
            # Check if the message is already encrypted; if not, encrypt it
            if not isinstance(value, bytes):
                value = self.encrypt_message(value)

            return self.producer.send(topic, value=value)
        except Exception as e:
            logger.error(f"Failed to send message to topic '{topic}': {e}")
            raise e

    def flush(self):
        """Flush all buffered Kafka messages."""
        try:
            self.producer.flush()
        except Exception as e:
            logger.error(f"Failed to flush KafkaProducer: {e}")
            raise e

    def send_message(self, topic_key, message):
        """Send a message to a topic using the topic key."""
        topic = settings.KAFKA_TOPICS.get(topic_key)
        if not topic:
            logger.error(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")
            raise ValueError(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")
        self.send(topic, message)

    def validate_and_send_message(self, topic_key, message):
        """Validate and send a structured message."""
        try:
            event_data = EventData.parse_obj(message)
            self.send_message(topic_key, event_data.dict())
        except ValidationError as e:
            logger.error(f"Validation error for message: {e}")
