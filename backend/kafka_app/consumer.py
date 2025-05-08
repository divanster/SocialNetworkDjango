import os
import django
import json
import logging
import asyncio

import jwt  # JWT for in-message token validation
from pydantic import ValidationError
from aiokafka import AIOKafkaConsumer
from cryptography.fernet import Fernet

from django.conf import settings
from django.db import close_old_connections
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from kafka_app.schemas import EventData
from kafka_app.constants import (
    ALBUM_CREATED, COMMENT_CREATED, FOLLOW_CREATED, FRIEND_ADDED,
    MESSAGE_EVENT, NEWSFEED_UPDATED, REACTION_ADDED, SOCIAL_ACTION,
    STORY_SHARED, TAG_ADDED, TAG_REMOVED, USER_REGISTERED,
    NOTIFICATION_SENT, POST_CREATED, POST_UPDATED, POST_DELETED,
)

# Ensure Django settings are loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)

class KafkaConsumerApp:
    """
    Async Kafka consumer powered by aiokafka.  Dispatches events to your services
    and forwards to Channels groups, with optional JWT in-message validation.
    """
    def __init__(self, topics, group_id):
        self.topics = topics if isinstance(topics, list) else [topics]
        self.group_id = group_id
        self.consumer = None
        self.channel_layer = get_channel_layer()
        self.handlers = self._load_handlers()

    def _load_handlers(self):
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

        def wrap(fn, group_name, label):
            def handler(data):
                fn(data)
                async_to_sync(self.channel_layer.group_send)(
                    group_name,
                    {"type": "kafka_message", "message": {"event": label, "data": data}}
                )
            return handler

        return {
            ALBUM_CREATED:    wrap(process_album_event,     "albums",       "New album created"),
            COMMENT_CREATED:  wrap(process_comment_event,   "comments",     "New comment posted"),
            FOLLOW_CREATED:   wrap(process_follow_event,    "follows",      "New follow event"),
            FRIEND_ADDED:     wrap(process_friend_event,    "friends",      "New friend added"),
            MESSAGE_EVENT:    wrap(process_messenger_event, "messenger",    "New message"),
            NEWSFEED_UPDATED: wrap(process_newsfeed_event,  "newsfeed",     "Newsfeed updated"),
            REACTION_ADDED:   wrap(process_reaction_event,  "reactions",    "New reaction added"),
            STORY_SHARED:     wrap(process_story_event,     "stories",      "New story shared"),
            TAG_ADDED:        wrap(process_tagging_event,   "tagging",      "New tag added"),
            TAG_REMOVED:      wrap(process_tagging_event,   "tagging",      "Tag removed"),
            USER_REGISTERED:  wrap(process_user_event,      "users",        "New user registered"),
            NOTIFICATION_SENT:wrap(create_notification,     "notifications","New notification"),
            POST_CREATED:     wrap(process_social_event,    "social",       "New post created"),
            POST_UPDATED:     wrap(process_social_event,    "social",       "Post updated"),
            POST_DELETED:     wrap(process_social_event,    "social",       "Post deleted"),
        }

    async def _consume_loop(self):
        # Initialize and start the aiokafka consumer
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            group_id=self.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self.consumer.start()
        logger.info(f"Started aiokafka consumer on topics: {self.topics}")

        try:
            async for msg in self.consumer:
                close_old_connections()

                raw = msg.value
                # Optional decryption
                if settings.KAFKA_ENCRYPTION_KEY:
                    cipher = Fernet(settings.KAFKA_ENCRYPTION_KEY.encode())
                    raw = cipher.decrypt(raw)

                # Parse JSON + validate structure
                try:
                    payload = json.loads(raw.decode('utf-8'))
                    event = EventData.parse_obj(payload)
                except (ValidationError, json.JSONDecodeError) as e:
                    logger.error(f"Invalid message payload: {e}")
                    continue

                # **JWT in-message validation**
                jwt_token = event.data.get("jwt_token")
                if jwt_token:
                    try:
                        jwt.decode(
                            jwt_token,
                            settings.SIMPLE_JWT['SIGNING_KEY'],
                            algorithms=['HS256'],
                            options={'verify_exp': True}
                        )
                    except jwt.ExpiredSignatureError:
                        logger.warning("Skipping message with expired JWT token")
                        continue
                    except jwt.DecodeError:
                        logger.warning("Skipping message with invalid JWT token")
                        continue

                # Dispatch to handler
                handler = self.handlers.get(event.event_type)
                if handler:
                    try:
                        handler(event.data)
                    except Exception as e:
                        logger.error(f"Error in handler for {event.event_type}: {e}", exc_info=True)
                else:
                    logger.warning(f"No handler for event type: {event.event_type}")

        finally:
            await self.consumer.stop()
            logger.info("aiokafka consumer stopped")

    def start(self):
        """
        Synchronously bootstrap the async consumer loop.
        """
        asyncio.run(self._consume_loop())
