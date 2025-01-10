# backend/kafka_app/consumer.py

import os
import logging
import json
import time
from pydantic import BaseModel, ValidationError
from kafka.errors import KafkaError
from django.db import close_old_connections
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from cryptography.fernet import Fernet

# Set up Django settings (this MUST be done before importing any Django models or services)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Now initialize Django
import django

django.setup()

# Import service handlers
from albums.services import process_album_event
from comments.services import process_comment_event
from follows.services import process_follow_event
from friends.services import process_friend_event
from messenger.services import process_messenger_event
from newsfeed.services import process_newsfeed_event
from reactions.services import process_reaction_event
from social.services import process_social_event
from stories.services import process_story_event
from tagging.services import process_tagging_event
from users.services import process_user_event
from notifications.services import create_notification

logger = logging.getLogger(__name__)


# Define the Pydantic model for message validation
class EventData(BaseModel):
    event_type: str
    data: dict

    class Config:
        min_anystr_length = 1  # Ensure non-empty strings


class BaseKafkaConsumer:
    """
    Base Kafka Consumer class to handle connection setup and basic consumption logic.
    """

    def __init__(self, topics, group_id):
        from kafka import KafkaConsumer
        self.topics = topics
        self.group_id = group_id
        self.consumer = KafkaConsumer(
            *self.topics,
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=self.group_id,
            # Removed value_deserializer to receive raw bytes
        )
        self.key = settings.KAFKA_ENCRYPTION_KEY.encode()
        self.cipher_suite = Fernet(self.key)

    def close(self):
        self.consumer.close()
        logger.info("Kafka consumer closed.")


class KafkaConsumerApp(BaseKafkaConsumer):
    """
    Kafka Consumer Application to handle different topics and event types.
    Inherits from BaseKafkaConsumer to reuse core Kafka setup and consumption logic.
    """

    def __init__(self, topics, group_id):
        # Initialize the base Kafka consumer with the given topics and group ID
        super().__init__(topics, group_id)
        self.handlers = self._load_handlers()
        self.channel_layer = get_channel_layer()

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
            'reaction_added': self.handle_reaction_event,
            'social_action': self.handle_social_event,
            'story_shared': self.handle_story_event,
            'tag_added': self.handle_tagging_event,
            'user_registered': self.handle_user_event,
            'notification_sent': self.handle_notification_event,
            'updated': self.handle_updated_event  # Handler for 'updated' event
        }

    def consume_messages(self):
        while True:
            try:
                logger.info(
                    f"Started consuming messages from topics: {', '.join(self.topics)}")
                for message in self.consumer:
                    close_old_connections()

                    if not message.value:
                        logger.warning(
                            f"Received an empty message from topic {message.topic}, skipping.")
                        continue

                    try:
                        logger.debug(f"Received encrypted message: {message.value}")
                        # Decrypt the message
                        decrypted_bytes = self.cipher_suite.decrypt(message.value)
                        decrypted_str = decrypted_bytes.decode('utf-8')
                        logger.debug(f"Decrypted message: {decrypted_str}")
                        # Parse JSON
                        message_data = json.loads(decrypted_str)
                        self.process_message(message_data)
                    except (ValidationError, json.JSONDecodeError) as e:
                        logger.error(f"Message validation or JSON decoding error: {e}")
                    except Exception as e:
                        logger.error(f"Failed to process message {message.value}: {e}",
                                     exc_info=True)
            except KafkaError as e:
                logger.error(f"Kafka consumer error: {e}. Retrying in 10 seconds...",
                             exc_info=True)
                time.sleep(10)
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                time.sleep(10)
            finally:
                self.close()

    def start(self):
        """
        Start consuming messages from Kafka.
        """
        self.consume_messages()

    def process_message(self, message):
        """
        Process incoming Kafka messages.
        """
        try:
            # Validate incoming message using Pydantic model
            event_data = EventData.parse_obj(message)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return

        # Extract event type and get the handler
        event_type = event_data.event_type
        handler = self.handlers.get(event_type)

        # Handle the event using the appropriate handler method
        if handler:
            try:
                # Call the specific handler for the event
                handler(event_data.data)

                # Forward the message to a WebSocket group if applicable
                group_name = event_data.data.get("group_name",
                                                 "default")  # Use 'default' if no group_name is provided
                self.send_to_websocket_group(group_name, event_data.data)
            except Exception as e:
                logger.error(f"Error processing event '{event_type}': {e}",
                             exc_info=True)
        else:
            logger.warning(f"No handler found for event type: {event_type}")

    def send_to_websocket_group(self, group_name, message):
        """
        Send a message to a specific WebSocket group.
        """
        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                "type": "kafka_message",  # Must match the consumer's method name
                "message": message,
            }
        )

    # Handlers for different event types
    def handle_messenger_event(self, data):
        process_messenger_event(data)
        self.send_to_websocket_group("messenger",
                                     {"event": "New message", "data": data})

    def handle_newsfeed_event(self, data):
        process_newsfeed_event(data)
        self.send_to_websocket_group("newsfeed",
                                     {"event": "Newsfeed updated", "data": data})

    def handle_album_event(self, data):
        process_album_event(data)
        self.send_to_websocket_group("albums",
                                     {"event": "New album created", "data": data})

    def handle_comment_event(self, data):
        process_comment_event(data)
        self.send_to_websocket_group("comments",
                                     {"event": "New comment posted", "data": data})

    def handle_follow_event(self, data):
        process_follow_event(data)
        self.send_to_websocket_group("follows",
                                     {"event": "New follow event", "data": data})

    def handle_friend_event(self, data):
        process_friend_event(data)
        self.send_to_websocket_group("friends",
                                     {"event": "New friend added", "data": data})

    def handle_reaction_event(self, data):
        process_reaction_event(data)
        self.send_to_websocket_group("reactions",
                                     {"event": "New reaction added", "data": data})

    def handle_social_event(self, data):
        process_social_event(data)
        # Determine the event for WebSocket based on event_type
        event_type = data.get('event_type')
        websocket_event = ""
        if event_type == 'post_created':
            websocket_event = "New post created"
        elif event_type == 'post_updated':
            websocket_event = "Post updated"
        elif event_type == 'post_deleted':
            websocket_event = "Post deleted"
        elif event_type == 'tagged':
            websocket_event = "New tag added"
        elif event_type == 'untagged':
            websocket_event = "Tag removed"
        else:
            websocket_event = f"Social event: {event_type}"

        self.send_to_websocket_group("social",
                                     {"event": websocket_event, "data": data})

    def handle_story_event(self, data):
        process_story_event(data)
        self.send_to_websocket_group("stories",
                                     {"event": "New story shared", "data": data})

    def handle_tagging_event(self, data):
        process_tagging_event(data)
        self.send_to_websocket_group("tagging",
                                     {"event": "New tag added", "data": data})

    def handle_user_event(self, data):
        process_user_event(data)
        self.send_to_websocket_group("users",
                                     {"event": "New user registered", "data": data})

    def handle_notification_event(self, data):
        create_notification(data)
        self.send_to_websocket_group("notifications",
                                     {"event": "New notification", "data": data})

    def handle_updated_event(self, data):
        """
        Handle 'updated' event type.
        Determines the entity being updated and processes accordingly.
        """
        entity = data.get('entity')
        if not entity:
            logger.warning("Received 'updated' event without 'entity' field.")
            return

        if entity == 'post':
            self.handle_post_update(data)
        elif entity == 'album':
            self.handle_album_update(data)
        elif entity == 'comment':
            self.handle_comment_update(data)
        else:
            logger.warning(f"Unknown entity type for 'updated' event: {entity}")

    def handle_post_update(self, data):
        """
        Handle update of a social post.
        """
        process_social_event(data)  # Processes post updates
        websocket_event = "Post updated"
        self.send_to_websocket_group("social", {"event": websocket_event, "data": data})

    def handle_album_update(self, data):
        """
        Handle update of an album.
        """
        process_album_event(data)  # Processes album updates
        websocket_event = "Album updated"
        self.send_to_websocket_group("albums", {"event": websocket_event, "data": data})

    def handle_comment_update(self, data):
        """
        Handle update of a comment.
        """
        process_comment_event(data)  # Processes comment updates
        websocket_event = "Comment updated"
        self.send_to_websocket_group("comments", {"event": websocket_event, "data": data})

# def handle_updated_event(self, data):
#     """
#     Handle 'updated' event type.
#     Determines the entity being updated and processes accordingly.
#     """
#     entity = data.get('entity')
#     if not entity:
#         logger.warning("Received 'updated' event without 'entity' field.")
#         return
#
#     if entity == 'post':
#         process_social_event(data)  # Assuming this processes post updates
#         websocket_event = "Post updated"
#         self.send_to_websocket_group("social",
#                                      {"event": websocket_event, "data": data})
#     elif entity == 'album':
#         process_album_event(data)  # Assuming this processes album updates
#         websocket_event = "Album updated"
#         self.send_to_websocket_group("albums",
#                                      {"event": websocket_event, "data": data})
#     elif entity == 'comment':
#         process_comment_event(data)  # Assuming this processes comment updates
#         websocket_event = "Comment updated"
#         self.send_to_websocket_group("comments",
#                                      {"event": websocket_event, "data": data})
#     else:
#         logger.warning(f"Unknown entity type for 'updated' event: {entity}")
