# kafka_app/consumer.py
from kafka import KafkaConsumer  # Importing the KafkaConsumer
from kafka.errors import KafkaError  # Correct import for KafkaError
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class KafkaConsumerClient:
    def __init__(self, topic_key):
        topic = settings.KAFKA_TOPICS.get(topic_key)
        if not topic:
            logger.error(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")
            raise ValueError(f"Topic '{topic_key}' not found in KAFKA_TOPICS.")

        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=[settings.KAFKA_BROKER_URL],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=settings.KAFKA_CONSUMER_GROUP_ID,
                # Assuming you add this to settings.py
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info(
                f"KafkaConsumer initialized for topic '{topic_key}' successfully.")
        except KafkaError as e:
            logger.error(
                f"Failed to initialize KafkaConsumer for topic '{topic_key}': {e}")
            raise e

    def consume_messages(self):
        try:
            for message in self.consumer:
                logger.info(f"Received message: {message.value}")
                # Implement message handling logic here
        except KafkaError as e:
            logger.error(f"Error consuming messages: {e}")
            raise e

    def close(self):
        if self.consumer:
            self.consumer.close()
            logger.info("KafkaConsumer connection closed.")
