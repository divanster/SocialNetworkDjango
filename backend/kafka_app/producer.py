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
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=5
            )
            self.key = settings.KAFKA_ENCRYPTION_KEY.encode()
            self.cipher_suite = Fernet(self.key)
            logger.info("KafkaProducer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize KafkaProducer: {e}")
            raise e

    def encrypt_message(self, message):
        message_bytes = json.dumps(message).encode('utf-8')
        encrypted_message = self.cipher_suite.encrypt(message_bytes)
        return encrypted_message

    def send_message(self, topic_key, message):
        topic = settings.KAFKA_TOPICS.get(topic_key)
        if not topic:
            logger.error(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")
            raise ValueError(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")
        try:
            encrypted_message = self.encrypt_message(message)
            self.producer.send(topic, value=encrypted_message)
            self.producer.flush()
            logger.info(f"Encrypted message sent to topic '{topic}': {message}")
        except Exception as e:
            logger.error(f"Failed to send message to topic '{topic}': {e}")
            raise e

    def validate_and_send_message(self, topic_key, message):
        try:
            # Validate the structure of the message before sending
            event_data = EventData.parse_obj(message)
            self.send_message(topic_key, event_data.dict())
        except ValidationError as e:
            logger.error(f"Validation error for message: {e}")
