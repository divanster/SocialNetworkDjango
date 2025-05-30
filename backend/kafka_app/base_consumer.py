import os
import time
import logging
import json
import django
import jwt  # Import jwt for decoding tokens
from pydantic import BaseModel, ValidationError  # Import BaseModel and ValidationError from Pydantic
from aiokafka.errors import KafkaError, KafkaConnectionError as NoBrokersAvailable, KafkaTimeoutError
from kafka import KafkaConsumer
from django.conf import settings
from django.db import close_old_connections
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EventData(BaseModel):
    """
    Pydantic model to validate incoming Kafka message data.
    """
    event_type: str
    data: dict


def get_backoff_time(retries):
    """
    Exponential backoff with jitter.
    """
    base = 2
    jitter = random.uniform(0.5, 1.5)
    return min(60, base ** retries) * jitter


class BaseKafkaConsumer:
    def __init__(self, topics, group_id):
        """
        Initialize the Base Kafka Consumer.

        Args:
            topics (list[str]): List of topics to subscribe to.
            group_id (str): Kafka consumer group ID.
        """
        self.setup_django()
        self.topics = topics if isinstance(topics, list) else [topics]
        self.group_id = group_id
        self.consumer = self.get_kafka_consumer()
        self.handlers = {}  # Ensure `handlers` is defined

    @staticmethod
    def setup_django():
        """
        Set up Django environment.
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
        Retries until max_retries are exceeded.
        """
        retries = 0
        max_retries = getattr(settings, 'KAFKA_MAX_RETRIES', 5)

        while retries < max_retries or max_retries == -1:
            try:
                logger.info(f"Connecting to Kafka at {settings.KAFKA_BROKER_URL} with topics: {', '.join(self.topics)}")
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
                wait_time = get_backoff_time(retries)
                logger.error(f"Failed to connect to Kafka: {e}. Retrying in {wait_time} seconds... ({retries}/{max_retries})")
                retries += 1
                time.sleep(wait_time)

        logger.error("Max retries exceeded. Could not connect to Kafka.")
        raise RuntimeError("Unable to connect to Kafka broker.")

    def consume_messages(self):
        """
        Start consuming messages from the Kafka topics.
        """
        while True:
            try:
                logger.info(f"Started consuming messages from topics: {', '.join(self.topics)}")
                for message in self.consumer:
                    close_old_connections()

                    if not message.value:
                        logger.warning(f"Received an empty message from topic {message.topic}, skipping.")
                        continue

                    try:
                        logger.info(f"Received message: {message.value}")
                        message_data = json.loads(message.value)
                        self.process_message(message_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode JSON message: {e}")
                    except Exception as e:
                        logger.error(f"Failed to process message {message.value}: {e}", exc_info=True)

            except KafkaError as e:
                logger.error(f"Kafka consumer error: {e}. Retrying in 10 seconds...", exc_info=True)
                time.sleep(10)

    def process_message(self, message):
        """
        Process an incoming message from Kafka.
        """
        try:
            # Validate incoming message using Pydantic model
            event_data = EventData.parse_obj(message)

            # Before processing, validate JWT token if required for this message type
            jwt_token = event_data.data.get("jwt_token")
            if jwt_token:
                try:
                    jwt.decode(jwt_token, settings.SIMPLE_JWT['SIGNING_KEY'],
                               algorithms=['HS256'], options={'verify_exp': True})
                except jwt.ExpiredSignatureError:
                    logger.warning("Received expired JWT token in Kafka message.")
                    return  # Skip processing this message
                except jwt.DecodeError:
                    logger.warning("Received invalid JWT token in Kafka message.")
                    return  # Skip processing this message

            # Process the event using the appropriate handler
            event_type = event_data.event_type
            handler = self.handlers.get(event_type)
            if handler:
                handler(event_data.data)
            else:
                logger.warning(f"No handler found for event type: {event_type}")

        except ValidationError as e:
            logger.error(f"Validation error: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

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
                logger.error(f"Error while closing Kafka consumer: {e}", exc_info=True)
