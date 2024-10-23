# backend/notifications/consumer.py
import os
import django
import time
import logging
import json
import sys
from kafka import KafkaConsumer
from django.conf import settings
from .services import create_notification

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)

class NotificationConsumer:
    def __init__(self):
        self.topic = settings.NOTIFICATIONS_TOPIC
        self.consumer = self.get_kafka_consumer()

    def get_kafka_consumer(self):
        retries = 0
        max_retries = getattr(settings, 'KAFKA_MAX_RETRIES', 5)
        while retries < max_retries or max_retries == -1:
            try:
                consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=settings.KAFKA_BROKER_URL,
                    group_id=settings.KAFKA_CONSUMER_GROUP_ID,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                logger.info(f"Connected to Kafka topic: {self.topic}")
                return consumer
            except Exception as e:
                logger.error(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
                retries += 1
                time.sleep(5)
        logger.error("Max retries exceeded. Could not connect to Kafka.")
        sys.exit(1)

    def consume_messages(self):
        try:
            for message in self.consumer:
                logger.info(f"Received message: {message.value}")
                self.process_notification(message.value)
        except Exception as e:
            logger.error(f"Error while consuming messages: {e}")
        finally:
            self.close()

    def process_notification(self, message):
        notification_type = message.get('event_type')
        sender_id = message.get('sender_id')
        sender_username = message.get('sender_username')
        receiver_id = message.get('receiver_id')
        receiver_username = message.get('receiver_username')
        text = message.get('message', '')

        # Use service to create a notification
        create_notification(
            sender_id=sender_id,
            sender_username=sender_username,
            receiver_id=receiver_id,
            receiver_username=receiver_username,
            notification_type=notification_type,
            text=text
        )

    def close(self):
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("Kafka consumer closed.")

if __name__ == "__main__":
    consumer = NotificationConsumer()
    consumer.consume_messages()
