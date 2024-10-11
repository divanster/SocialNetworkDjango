import os
import django
import time
import logging
from kafka import KafkaConsumer
from django.conf import settings
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)


class KafkaPostConsumer:
    def __init__(self, topic):
        self.topic = topic
        self.consumer = self.get_kafka_consumer()

    def get_kafka_consumer(self):
        while True:
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
                logger.error(
                    f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def consume_messages(self):
        for message in self.consumer:
            try:
                # Extract message value and perform custom processing logic
                logger.info(f"Received message from Kafka: {message.value}")

                # Add your processing logic for the post event here
                self.process_post_event(message.value)

            except Exception as e:
                logger.error(f"Error processing message: {e}")

    def process_post_event(self, message):
        """
        Process the post event message.
        """
        try:
            event_type = message.get('event')
            post_id = message.get('post_id')
            logger.info(
                f"Processing post event of type '{event_type}' for Post ID: {post_id}")

            # Implement specific actions for created, updated, and deleted events
            if event_type == 'created':
                self.handle_created_post(message)
            elif event_type == 'updated':
                self.handle_updated_post(message)
            elif event_type == 'deleted':
                self.handle_deleted_post(message)
            else:
                logger.warning(f"Unknown event type received: {event_type}")

        except KeyError as e:
            logger.error(f"Missing required key in Kafka message: {e}")
        except Exception as e:
            logger.error(f"Error while processing post event: {e}")

    def handle_created_post(self, message):
        """
        Logic to handle a created post event.
        """
        logger.info(f"Handling post creation event: {message}")

    def handle_updated_post(self, message):
        """
        Logic to handle an updated post event.
        """
        logger.info(f"Handling post update event: {message}")

    def handle_deleted_post(self, message):
        """
        Logic to handle a deleted post event.
        """
        logger.info(f"Handling post deletion event: {message}")


def main():
    topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')
    consumer_client = KafkaPostConsumer(topic)
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
