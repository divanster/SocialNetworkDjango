import os
import time
import logging
import json
import sys
from kafka import KafkaConsumer
from django.db import close_old_connections

logger = logging.getLogger(__name__)


class KafkaConsumerClient:
    def __init__(self, topics):
        """
        :param topics: list of topics to subscribe to.
        """
        from django.conf import settings  # Import after django.setup()
        self.settings = settings
        self.topics = topics
        self.consumer = self.get_kafka_consumer()

    def get_kafka_consumer(self):
        retries = 0
        max_retries = getattr(self.settings, 'KAFKA_MAX_RETRIES', 5)
        wait_time = 5  # seconds

        while retries < max_retries or max_retries == -1:
            try:
                consumer = KafkaConsumer(
                    *self.topics,  # Accept multiple topics
                    bootstrap_servers=self.settings.KAFKA_BROKER_URL,
                    group_id=self.settings.KAFKA_CONSUMER_GROUP_ID,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                logger.info(f"Connected to Kafka topics: {', '.join(self.topics)}")
                return consumer
            except Exception as e:
                logger.error(f"Failed to connect to Kafka: {e}. Retrying in {wait_time} seconds...")
                retries += 1
                time.sleep(wait_time)

        logger.error("Max retries exceeded. Could not connect to Kafka.")
        sys.exit(1)  # Stop the script if setup fails

    def consume_messages(self):
        try:
            for message in self.consumer:
                close_old_connections()  # Ensure fresh database connections
                logger.info(f"Received message from topic {message.topic}: {message.value}")
                self.process_message(message.topic, message.value)
        except Exception as e:
            logger.error(f"Error while consuming messages: {e}")
        finally:
            self.close()

    def process_message(self, topic, message):
        """
        Process the message depending on the topic it came from.
        """
        try:
            logger.info(f"Processing message from topic '{topic}': {message}")
            # Your actual message processing code here
            if topic == self.settings.KAFKA_TOPICS['ALBUM_EVENTS']:
                self.handle_album_event(message)
            elif topic == self.settings.KAFKA_TOPICS['COMMENT_EVENTS']:
                self.handle_comment_event(message)
            elif topic == self.settings.KAFKA_TOPICS['FOLLOW_EVENTS']:
                self.handle_follow_event(message)
            elif topic == self.settings.KAFKA_TOPICS['FRIEND_EVENTS']:
                self.handle_friend_event(message)
            elif topic == self.settings.KAFKA_TOPICS['MESSENGER_EVENTS']:
                self.handle_messenger_event(message)
            elif topic == self.settings.KAFKA_TOPICS['NEWSFEED_EVENTS']:
                self.handle_newsfeed_event(message)
            elif topic == self.settings.KAFKA_TOPICS['PAGE_EVENTS']:
                self.handle_page_event(message)
            elif topic == self.settings.KAFKA_TOPICS['REACTION_EVENTS']:
                self.handle_reaction_event(message)
            elif topic == self.settings.KAFKA_TOPICS['SOCIAL_EVENTS']:
                self.handle_social_event(message)
            elif topic == self.settings.KAFKA_TOPICS['STORY_EVENTS']:
                self.handle_story_event(message)
            elif topic == self.settings.KAFKA_TOPICS['TAGGING_EVENTS']:
                self.handle_tagging_event(message)
            elif topic == self.settings.KAFKA_TOPICS['USER_EVENTS']:
                self.handle_user_event(message)
            elif topic == self.settings.KAFKA_TOPICS['NOTIFICATIONS']:
                self.handle_notification_event(message)
            else:
                logger.warning(f"No handler found for topic: {topic}")
        except Exception as e:
            logger.error(f"Error processing message from topic '{topic}': {e}")

    # Handlers for each topic

    def handle_album_event(self, message):
        logger.info(f"Handling album event: {message}")

    def handle_comment_event(self, message):
        logger.info(f"Handling comment event: {message}")

    def handle_follow_event(self, message):
        logger.info(f"Handling follow event: {message}")

    def handle_friend_event(self, message):
        logger.info(f"Handling friend event: {message}")

    def handle_messenger_event(self, message):
        logger.info(f"Handling messenger event: {message}")

    def handle_newsfeed_event(self, message):
        logger.info(f"Handling newsfeed event: {message}")

    def handle_page_event(self, message):
        logger.info(f"Handling page event: {message}")

    def handle_reaction_event(self, message):
        logger.info(f"Handling reaction event: {message}")

    def handle_social_event(self, message):
        logger.info(f"Handling social event: {message}")

    def handle_story_event(self, message):
        logger.info(f"Handling story event: {message}")

    def handle_tagging_event(self, message):
        logger.info(f"Handling tagging event: {message}")

    def handle_user_event(self, message):
        logger.info(f"Handling user event: {message}")

    def handle_notification_event(self, message):
        logger.info(f"Handling notification event: {message}")

    def close(self):
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("Kafka consumer closed.")


def main():
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    try:
        django.setup()
        logger.info("Django setup completed successfully.")
    except Exception as e:
        logger.error(f"Failed to set up Django: {e}")
        sys.exit(1)

    from django.conf import settings

    topics = [
        settings.KAFKA_TOPICS['ALBUM_EVENTS'],
        settings.KAFKA_TOPICS['COMMENT_EVENTS'],
        settings.KAFKA_TOPICS['FOLLOW_EVENTS'],
        settings.KAFKA_TOPICS['FRIEND_EVENTS'],
        settings.KAFKA_TOPICS['MESSENGER_EVENTS'],
        settings.KAFKA_TOPICS['NEWSFEED_EVENTS'],
        settings.KAFKA_TOPICS['PAGE_EVENTS'],
        settings.KAFKA_TOPICS['REACTION_EVENTS'],
        settings.KAFKA_TOPICS['SOCIAL_EVENTS'],
        settings.KAFKA_TOPICS['STORY_EVENTS'],
        settings.KAFKA_TOPICS['TAGGING_EVENTS'],
        settings.KAFKA_TOPICS['USER_EVENTS'],
        settings.KAFKA_TOPICS['NOTIFICATIONS']
    ]

    consumer_client = KafkaConsumerClient(topics)
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
