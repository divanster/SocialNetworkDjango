# backend/kafka_app/producer.py

import json
import uuid
import logging
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

class KafkaProducerClient:
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[settings.KAFKA_BROKER_URL],
                retries=5,
                # We'll do custom JSON + encryption in `encrypt_message`.
            )
            self.key = settings.KAFKA_ENCRYPTION_KEY.encode()
            self.cipher_suite = Fernet(self.key)
            logger.info("KafkaProducer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize KafkaProducer: {e}")
            raise e

    def encrypt_message(self, message):
        """
        Encrypts a message. The 'message' can contain raw UUID.
        We call json.dumps(..., cls=UUIDEncoder) to handle them.
        """
        try:
            json_bytes = json.dumps(message, cls=UUIDEncoder).encode('utf-8')
            encrypted = self.cipher_suite.encrypt(json_bytes)
            return encrypted
        except Exception as e:
            logger.error(f"Error encrypting message: {e}")
            raise e

    def send(self, topic, value):
        """
        Sends 'value' to Kafka, ensuring we do encryption + UUIDEncoder.
        """
        try:
            if not isinstance(value, bytes):
                # if it's a dict, we do encryption:
                value = self.encrypt_message(value)

            return self.producer.send(topic, value=value)
        except Exception as e:
            logger.error(f"Failed to send message to topic '{topic}': {e}")
            raise e

    def flush(self):
        try:
            self.producer.flush()
        except Exception as e:
            logger.error(f"Failed to flush KafkaProducer: {e}")
            raise e

    def close(self):
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed.")
