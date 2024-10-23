# consumer.py

import os
import sys
import time
import logging
import json
from kafka import KafkaConsumer

# Set up Django settings (this MUST be done before importing any Django models or services)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Now initialize Django
import django

django.setup()

from django.db import close_old_connections
from django.conf import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Now import the services and models after setting up Django
from albums.services import process_album_event
from comments.services import process_comment_event
from follows.services import process_follow_event
from friends.services import process_friend_event
from messenger.services import process_messenger_event
from newsfeed.services import process_newsfeed_event
from pages.services import process_page_event
from reactions.services import process_reaction_event
from social.services import process_social_event
from stories.services import process_story_event
from tagging.services import process_tagging_event
from users.services import process_user_event
from notifications.services import create_notification


class KafkaConsumerApp:
    def __init__(self):
        """
        Initialize the Kafka consumer to listen to the consolidated topics.
        """
        self.topics = list(settings.KAFKA_TOPICS.values())
        self.consumer = self.get_kafka_consumer()
        self.handlers = self._load_handlers()

    def get_kafka_consumer(self):
        retries = 0
        max_retries = getattr(settings, 'KAFKA_MAX_RETRIES', 5)
        wait_time = 5  # seconds

        while retries < max_retries or max_retries == -1:
            try:
                consumer = KafkaConsumer(
                    *self.topics,
                    bootstrap_servers=settings.KAFKA_BROKER_URL,
                    group_id=settings.KAFKA_CONSUMER_GROUP_ID,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                logger.info(f"Connected to Kafka topics: {self.topics}")
                return consumer
            except Exception as e:
                logger.error(
                    f"Failed to connect to Kafka: {e}. Retrying in {wait_time} seconds...")
                retries += 1
                time.sleep(wait_time)

        logger.error("Max retries exceeded. Could not connect to Kafka.")
        sys.exit(1)  # Stop the script if setup fails

    def _load_handlers(self):
        """
        Load handlers that will process different event types.
        """
        return {
            'album_created': self.handle_album_event,
            'comment_posted': self.handle_comment_event,
            'follow_created': self.handle_follow_event,
            'friend_added': self.handle_friend_event,
            'message_event': self.handle_messenger_event,
            'newsfeed_updated': self.handle_newsfeed_event,
            'page_created': self.handle_page_event,
            'reaction_added': self.handle_reaction_event,
            'social_action': self.handle_social_event,
            'story_shared': self.handle_story_event,
            'tag_added': self.handle_tagging_event,
            'user_registered': self.handle_user_event,
            'notification_sent': self.handle_notification_event
        }

    def consume_messages(self):
        try:
            for message in self.consumer:
                close_old_connections()  # Ensure fresh DB connections
                logger.info(f"Received message: {message.value}")
                self.process_message(message.value)
        except Exception as e:
            logger.error(f"Error while consuming messages: {e}", exc_info=True)
        finally:
            self.close()

    def process_message(self, message):
        event_type = message.get('event_type')
        handler = self.handlers.get(event_type)

        if handler:
            try:
                handler(message['data'])
            except Exception as e:
                logger.error(f"Error processing event '{event_type}': {e}",
                             exc_info=True)
        else:
            logger.warning(f"No handler found for event type: {event_type}")

    # Handlers for different event types

    def handle_album_event(self, data):
        process_album_event(data)
        create_notification(data)

    def handle_comment_event(self, data):
        process_comment_event(data)
        create_notification(data)

    def handle_follow_event(self, data):
        process_follow_event(data)
        create_notification(data)

    def handle_friend_event(self, data):
        process_friend_event(data)
        create_notification(data)

    def handle_messenger_event(self, data):
        process_messenger_event(data)

    def handle_newsfeed_event(self, data):
        process_newsfeed_event(data)

    def handle_page_event(self, data):
        process_page_event(data)

    def handle_reaction_event(self, data):
        process_reaction_event(data)
        create_notification(data)

    def handle_social_event(self, data):
        process_social_event(data)

    def handle_story_event(self, data):
        process_story_event(data)

    def handle_tagging_event(self, data):
        process_tagging_event(data)

    def handle_user_event(self, data):
        process_user_event(data)

    def handle_notification_event(self, data):
        create_notification(data)

    def close(self):
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("Kafka consumer closed.")


if __name__ == "__main__":
    consumer_app = KafkaConsumerApp()
    consumer_app.consume_messages()
