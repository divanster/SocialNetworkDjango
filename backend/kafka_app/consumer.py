# backend/kafka_app/consumer.py

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

from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from kafka_app.schemas import EventData
from kafka_app.constants import (
    USER_REGISTERED,
    ALBUM_CREATED, ALBUM_UPDATED, ALBUM_DELETED,
    COMMENT_CREATED, COMMENT_UPDATED, COMMENT_DELETED,
    FOLLOW_CREATED, FOLLOW_DELETED,
    FRIEND_ADDED, FRIEND_REMOVED,
    MESSAGE_EVENT,
    NEWSFEED_CREATED, NEWSFEED_UPDATED, NEWSFEED_DELETED,
    REACTION_ADDED, REACTION_CREATED, REACTION_UPDATED, REACTION_DELETED,
    TAG_ADDED, TAG_REMOVED,
    NOTIFICATION_SENT,
    POST_CREATED, POST_UPDATED, POST_DELETED,
)

# Ensure Django settings are loaded before anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)


class KafkaConsumerApp:
    """
    Async Kafka consumer powered by aiokafka.
    Dispatches events to your sync services and forwards to Channels groups,
    with optional JWT in‐message validation.
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

        def make_async_handler(fn, group_name, label, event_type_key):
            """
            Wrap a sync fn(data) as an async handler:
              1) inject `event_type` into data
              2) run fn(data) in threadpool via sync_to_async
              3) await group_send
            """
            async def handler(data):
                # 1. copy & inject the real event_type
                data = dict(data)
                data["event_type"] = event_type_key

                # 2. run your sync business logic
                await sync_to_async(fn)(data)

                # 3. broadcast over WebSocket
                await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": "kafka_message",
                        "message": {"event": label, "data": data},
                    },
                )
            return handler

        h = {
            # Albums
            ALBUM_CREATED: make_async_handler(process_album_event, "albums", "New album created", ALBUM_CREATED),
            ALBUM_UPDATED: make_async_handler(process_album_event, "albums", "Album updated",       ALBUM_UPDATED),
            ALBUM_DELETED: make_async_handler(process_album_event, "albums", "Album deleted",       ALBUM_DELETED),

            # Comments
            COMMENT_CREATED: make_async_handler(process_comment_event, "comments", "New comment", COMMENT_CREATED),
            COMMENT_UPDATED: make_async_handler(process_comment_event, "comments", "Comment updated", COMMENT_UPDATED),
            COMMENT_DELETED: make_async_handler(process_comment_event, "comments", "Comment deleted", COMMENT_DELETED),

            # Follows
            FOLLOW_CREATED: make_async_handler(process_follow_event, "follows", "New follow", FOLLOW_CREATED),
            FOLLOW_DELETED: make_async_handler(process_follow_event, "follows", "Follow removed", FOLLOW_DELETED),

            # Friends
            FRIEND_ADDED:   make_async_handler(process_friend_event, "friends", "New friend", FRIEND_ADDED),
            FRIEND_REMOVED: make_async_handler(process_friend_event, "friends", "Friend removed", FRIEND_REMOVED),

            # Messenger
            MESSAGE_EVENT: make_async_handler(process_messenger_event, "messenger", "New message", MESSAGE_EVENT),

            # Newsfeed
            NEWSFEED_CREATED: make_async_handler(process_newsfeed_event, "newsfeed", "Feed item created", NEWSFEED_CREATED),
            NEWSFEED_UPDATED: make_async_handler(process_newsfeed_event, "newsfeed", "Feed updated",      NEWSFEED_UPDATED),
            NEWSFEED_DELETED: make_async_handler(process_newsfeed_event, "newsfeed", "Feed removed",      NEWSFEED_DELETED),

            # Reactions
            REACTION_ADDED:   make_async_handler(process_reaction_event, "reactions", "Reaction added",   REACTION_ADDED),
            REACTION_CREATED: make_async_handler(process_reaction_event, "reactions", "New reaction",     REACTION_CREATED),
            REACTION_UPDATED: make_async_handler(process_reaction_event, "reactions", "Reaction updated", REACTION_UPDATED),
            REACTION_DELETED: make_async_handler(process_reaction_event, "reactions", "Reaction deleted", REACTION_DELETED),

            # Tagging
            TAG_ADDED:   make_async_handler(process_tagging_event, "tagging", "Tag added",   TAG_ADDED),
            TAG_REMOVED: make_async_handler(process_tagging_event, "tagging", "Tag removed", TAG_REMOVED),

            # Notifications
            NOTIFICATION_SENT: make_async_handler(create_notification, "notifications", "Notification sent", NOTIFICATION_SENT),

            # Social (Posts)
            POST_CREATED: make_async_handler(process_social_event, "social", "New post created", POST_CREATED),
            POST_UPDATED: make_async_handler(process_social_event, "social", "Post updated",       POST_UPDATED),
            POST_DELETED: make_async_handler(process_social_event, "social", "Post deleted",       POST_DELETED),
        }

        # backwards‐compat for producer keys:
        h["user_created"]           = h.get(USER_REGISTERED)
        h["post_newsfeed_created"]  = h.get(NEWSFEED_CREATED)

        return h

    async def _consume_loop(self):
        # 0) auto-create missing topics
        admin = AIOKafkaAdminClient(bootstrap_servers=settings.KAFKA_BROKER_URL)
        await admin.start()
        existing = await admin.list_topics()
        missing = [t for t in self.topics if t not in existing]
        if missing:
            await admin.create_topics([
                NewTopic(name=t, num_partitions=1, replication_factor=1)
                for t in missing
            ])
        await admin.close()

        # 1) now start your consumer as before
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            group_id=self.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            # you can tune these if you get rebalance errors
            max_poll_records=10,
            max_poll_interval_ms=300000,
        )
        await self.consumer.start()
        logger.info(f"Started aiokafka consumer on1 topics: {self.topics}")

        try:
            async for msg in self.consumer:
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

                # Optional in‐message JWT validation
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

                # Dispatch to the appropriate handler
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
        """Blocking entry‐point to run the async consumer loop."""
        asyncio.run(self._consume_loop())
