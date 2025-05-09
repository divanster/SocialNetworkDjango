# kafka_app/consumer.py

import os
import django
import json
import logging
import asyncio

import jwt  # JWT for in‐message token validation
from pydantic import ValidationError
from aiokafka import AIOKafkaConsumer
from cryptography.fernet import Fernet

from django.conf import settings
from django.db import close_old_connections
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

from kafka_app.schemas import EventData
from kafka_app.constants import (
    ALBUM_CREATED, COMMENT_CREATED, FOLLOW_CREATED, FRIEND_ADDED,
    MESSAGE_EVENT, NEWSFEED_UPDATED, REACTION_ADDED, SOCIAL_ACTION,
    STORY_SHARED, TAG_ADDED, TAG_REMOVED, USER_REGISTERED,
    NOTIFICATION_SENT, POST_CREATED, POST_UPDATED, POST_DELETED,
)

# Ensure Django settings are loaded before anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)


class KafkaConsumerApp:
    """
    Async Kafka consumer powered by aiokafka.  Dispatches events to your services
    and forwards to Channels groups, with optional JWT in‐message validation.
    """
    def __init__(self, topics, group_id):
        self.topics = topics if isinstance(topics, list) else [topics]
        self.group_id = group_id
        self.consumer = None
        self.channel_layer = get_channel_layer()
        self.handlers = self._load_handlers()

    def _load_handlers(self):
        # import your sync‐style business logic
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

        def make_async_handler(fn, group_name, label):
            """
            Wrap a sync fn(data) as an async handler:
              1) run fn in the threadpool via sync_to_async
              2) await group_send on channel_layer
            """
            async def handler(data):
                # 1. your business logic
                await sync_to_async(fn)(data)
                # 2. broadcast over WebSocket
                await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": "kafka_message",
                        "message": {"event": label, "data": data},
                    },
                )
            return handler

        h = {
            # Core events
            ALBUM_CREATED:     make_async_handler(process_album_event,     "albums",       "New album created"),
            COMMENT_CREATED:   make_async_handler(process_comment_event,   "comments",     "New comment posted"),
            FOLLOW_CREATED:    make_async_handler(process_follow_event,    "follows",      "New follow event"),
            FRIEND_ADDED:      make_async_handler(process_friend_event,    "friends",      "New friend added"),
            MESSAGE_EVENT:     make_async_handler(process_messenger_event, "messenger",    "New message"),
            NEWSFEED_UPDATED:  make_async_handler(process_newsfeed_event,  "newsfeed",     "Newsfeed updated"),
            REACTION_ADDED:    make_async_handler(process_reaction_event,  "reactions",    "New reaction added"),
            STORY_SHARED:      make_async_handler(process_story_event,     "stories",      "New story shared"),
            TAG_ADDED:         make_async_handler(process_tagging_event,   "tagging",      "New tag added"),
            TAG_REMOVED:       make_async_handler(process_tagging_event,   "tagging",      "Tag removed"),
            USER_REGISTERED:   make_async_handler(process_user_event,      "users",        "New user registered"),
            NOTIFICATION_SENT: make_async_handler(create_notification,     "notifications","New notification"),
            POST_CREATED:      make_async_handler(process_social_event,    "social",       "New post created"),
            POST_UPDATED:      make_async_handler(process_social_event,    "social",       "Post updated"),
            POST_DELETED:      make_async_handler(process_social_event,    "social",       "Post deleted"),
        }

        # The two that didn’t match your payload names:
        # (1) your producer emits "user_created" but your constant is probably "user_registered"
        h["user_created"] = h.get(USER_REGISTERED)
        # (2) your producer emits "post_newsfeed_created" but your constant is NEWSFEED_UPDATED
        h["post_newsfeed_created"] = h.get(NEWSFEED_UPDATED)

        return h

    async def _consume_loop(self):
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
                # recycle Django DB connections on each loop
                close_old_connections()

                raw = msg.value
                if settings.KAFKA_ENCRYPTION_KEY:
                    cipher = Fernet(settings.KAFKA_ENCRYPTION_KEY.encode())
                    raw = cipher.decrypt(raw)

                # JSON‐decode + Pydantic validation
                try:
                    payload = json.loads(raw.decode("utf-8"))
                    event = EventData.parse_obj(payload)
                except (ValidationError, json.JSONDecodeError) as e:
                    logger.error(f"Invalid message payload: {e}")
                    continue

                # optional in‐message JWT check
                tok = event.data.get("jwt_token")
                if tok:
                    try:
                        jwt.decode(
                            tok,
                            settings.SIMPLE_JWT["SIGNING_KEY"],
                            algorithms=["HS256"],
                            options={"verify_exp": True},
                        )
                    except jwt.ExpiredSignatureError:
                        logger.warning("Skipping expired JWT in event")
                        continue
                    except jwt.DecodeError:
                        logger.warning("Skipping invalid JWT in event")
                        continue

                # dispatch to the appropriate handler
                handler = self.handlers.get(event.event_type)
                if handler:
                    try:
                        await handler(event.data)
                    except Exception as e:
                        logger.error(f"Error in handler for {event.event_type}: {e}", exc_info=True)
                else:
                    logger.warning(f"No handler for event type: {event.event_type}")
        finally:
            await self.consumer.stop()
            logger.info("aiokafka consumer stopped")

    def start(self):
        """Block and run the async consumer loop."""
        asyncio.run(self._consume_loop())
