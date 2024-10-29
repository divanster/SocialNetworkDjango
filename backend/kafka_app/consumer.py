# backend/kafka_app/consumer.py

import os
import logging
import json
import time
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

# Import BaseKafkaConsumer to avoid code duplication
from .base_consumer import BaseKafkaConsumer

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


class KafkaConsumerApp(BaseKafkaConsumer):
    """
    Kafka Consumer Application to handle different topics and event types.
    Inherits from BaseKafkaConsumer to reuse core Kafka setup and consumption logic.
    """
    def __init__(self):
        super().__init__(topic=list(settings.KAFKA_TOPICS.values()), group_id=settings.KAFKA_CONSUMER_GROUP_ID)
        self.handlers = self._load_handlers()

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

    def process_message(self, message):
        """
        Process incoming Kafka messages.
        """
        event_type = message.get('event_type')
        handler = self.handlers.get(event_type)

        if handler:
            try:
                handler(message['data'])
            except Exception as e:
                logger.error(f"Error processing event '{event_type}': {e}", exc_info=True)
        else:
            logger.warning(f"No handler found for event type: {event_type}")

    # Handlers for different event types

    def handle_album_event(self, data):
        """
        Handle album-related events.
        """
        process_album_event(data)
        create_notification(data)

    def handle_comment_event(self, data):
        """
        Handle comment-related events.
        """
        process_comment_event(data)
        create_notification(data)

    def handle_follow_event(self, data):
        """
        Handle follow-related events.
        """
        process_follow_event(data)
        create_notification(data)

    def handle_friend_event(self, data):
        """
        Handle friend-related events.
        """
        process_friend_event(data)
        create_notification(data)

    def handle_messenger_event(self, data):
        """
        Handle messenger-related events.
        """
        process_messenger_event(data)

    def handle_newsfeed_event(self, data):
        """
        Handle newsfeed-related events.
        """
        process_newsfeed_event(data)

    def handle_page_event(self, data):
        """
        Handle page-related events.
        """
        process_page_event(data)

    def handle_reaction_event(self, data):
        """
        Handle reaction-related events.
        """
        process_reaction_event(data)
        create_notification(data)

    def handle_social_event(self, data):
        """
        Handle social-related events.
        """
        process_social_event(data)

    def handle_story_event(self, data):
        """
        Handle story-related events.
        """
        process_story_event(data)

    def handle_tagging_event(self, data):
        """
        Handle tagging-related events.
        """
        process_tagging_event(data)

    def handle_user_event(self, data):
        """
        Handle user-related events.
        """
        process_user_event(data)

    def handle_notification_event(self, data):
        """
        Handle notification-related events.
        """
        create_notification(data)


if __name__ == "__main__":
    consumer_app = KafkaConsumerApp()
    consumer_app.consume_messages()
