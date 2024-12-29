# backend/kafka_app/producer.py

import json
import uuid
import logging
from kafka import KafkaProducer
from django.conf import settings
from cryptography.fernet import Fernet
from threading import Lock

logger = logging.getLogger(__name__)


class UUIDEncoder(json.JSONEncoder):
    """
    Converts UUID objects to strings before JSON encoding.
    """

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


class KafkaProducerClient:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(KafkaProducerClient, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[settings.KAFKA_BROKER_URL],
                retries=5,
                # Removed value_serializer to handle serialization manually
            )
            self.key = settings.KAFKA_ENCRYPTION_KEY.encode()
            self.cipher_suite = Fernet(self.key)
            logger.info("KafkaProducer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize KafkaProducer: {e}")
            raise e

    def encrypt_message(self, message):
        """
        Encrypts a message. The 'message' should be a dictionary.
        """
        try:
            json_bytes = json.dumps(message, cls=UUIDEncoder).encode('utf-8')
            encrypted = self.cipher_suite.encrypt(json_bytes)
            return encrypted
        except Exception as e:
            logger.error(f"Error encrypting message: {e}")
            raise e

    def send_message(self, topic, value):
        """
        Sends 'value' to Kafka, ensuring serialization and encryption.
        """
        logger.info(f"send_message called with topic: {topic} and value: {value}")
        logger.info(f"self.producer type: {type(self.producer)}")  # Confirm type
        try:
            if not isinstance(value, bytes):
                value = self.encrypt_message(value)

            future = self.producer.send(topic, value=value)  # Send raw bytes
            result = future.get(timeout=10)  # Wait for send to complete
            logger.info(f"Message sent to topic '{topic}': {value}")
            return result
        except Exception as e:
            logger.error(f"Failed to send message to topic '{topic}': {e}")
            raise e

    def flush(self):
        try:
            self.producer.flush()
            logger.info("KafkaProducer flush completed.")
        except Exception as e:
            logger.error(f"Failed to flush KafkaProducer: {e}")
            raise e

    def close(self):
        try:
            self.producer.close(timeout=10)
            logger.info("KafkaProducer closed.")
        except Exception as e:
            logger.error(f"Failed to close KafkaProducer: {e}")
            raise e
