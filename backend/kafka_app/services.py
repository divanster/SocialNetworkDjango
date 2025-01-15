# backend/kafka_app/services.py

import json
import logging
import threading
import uuid
from kafka import KafkaProducer
from django.conf import settings
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class UUIDEncoder(json.JSONEncoder):
    """
    Converts UUID objects to strings before JSON encoding.
    """
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


class KafkaService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(KafkaService, cls).__new__(cls)
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

    def send_message(self, topic_key, message, retries=3):
        """
        Sends 'message' to Kafka after encryption.
        Retries on failure up to 'retries' times.
        """
        logger.info(f"send_message called with topic_key: {topic_key} and message: {message}")
        attempt = 0
        while attempt < retries:
            try:
                topic = settings.KAFKA_TOPICS.get(topic_key)
                if not topic:
                    raise ValueError(f"Topic key '{topic_key}' not found in KAFKA_TOPICS settings.")

                encrypted_message = self.encrypt_message(message)
                future = self.producer.send(topic, value=encrypted_message)
                result = future.get(timeout=10)  # Wait for send to complete
                logger.info(f"Message sent to topic '{topic}': {message}")
                return result
            except Exception as e:
                attempt += 1
                logger.error(f"Attempt {attempt}: Failed to send message to topic '{topic_key}': {e}")
                if attempt >= retries:
                    logger.error(f"Exceeded maximum retries ({retries}) for sending message to topic '{topic_key}'.")
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
            if hasattr(self, 'producer') and self.producer is not None:
                self.producer.flush()
                self.producer.close(timeout=10)
                self.producer = None
                logger.info("KafkaProducer closed.")
        except Exception as e:
            logger.error(f"Failed to close KafkaProducer: {e}")
            raise e
