import os
import django
import json
import logging
import asyncio

import jwt
from pydantic import ValidationError
from aiokafka import AIOKafkaConsumer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from cryptography.fernet import Fernet

from django.conf import settings
from django.db import close_old_connections
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

from kafka_app.schemas import EventData
from kafka_app.constants import (
    USER_REGISTERED, ALBUM_CREATED, ALBUM_UPDATED, ALBUM_DELETED,
    COMMENT_CREATED, COMMENT_UPDATED, COMMENT_DELETED, FOLLOW_CREATED, FOLLOW_DELETED,
    FRIEND_ADDED, FRIEND_REMOVED, MESSAGE_EVENT, NEWSFEED_CREATED, NEWSFEED_UPDATED, NEWSFEED_DELETED,
    REACTION_ADDED, REACTION_CREATED, REACTION_UPDATED, REACTION_DELETED,
    TAG_ADDED, TAG_REMOVED, NOTIFICATION_SENT, POST_CREATED, POST_UPDATED, POST_DELETED,
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logger = logging.getLogger(__name__)

from social.services import process_social_event
from social.models import Post


def handle_post_created(data: dict):
    post_id = data.get("id")
    if not post_id:
        logger.error(f"[KafkaConsumer] Missing post_id in event data: {data}")
        return

    post = Post.objects.filter(id=post_id).first()
    if not post:
        logger.error(f"[KafkaConsumer] Post ID {post_id} not found.")
        return

    event_payload = {
        "event_type": "post_created",
        "post_id": post_id,
        "user_id": str(post.user.id),
        "username": post.user.username,
        "title": post.title,
        "content": post.content,
        "visibility": post.visibility,
        "created_at": post.created_at.isoformat(),
    }

    process_social_event(event_payload)


class KafkaConsumerApp:
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
        from tagging.services import process_tagging_event
        from notifications.services import create_notification

        def make_async_handler(fn, group_name, label, event_type_key):
            async def handler(data):
                data["event_type"] = event_type_key
                await sync_to_async(fn)(data)
                await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": "kafka_message",
                        "message": {"event": label, "data": data},
                    },
                )
            return handler

        handlers = {
            ALBUM_CREATED: make_async_handler(process_album_event, "albums", "New album created", ALBUM_CREATED),
            ALBUM_UPDATED: make_async_handler(process_album_event, "albums", "Album updated", ALBUM_UPDATED),
            ALBUM_DELETED: make_async_handler(process_album_event, "albums", "Album deleted", ALBUM_DELETED),
            COMMENT_CREATED: make_async_handler(process_comment_event, "comments", "New comment", COMMENT_CREATED),
            COMMENT_UPDATED: make_async_handler(process_comment_event, "comments", "Comment updated", COMMENT_UPDATED),
            COMMENT_DELETED: make_async_handler(process_comment_event, "comments", "Comment deleted", COMMENT_DELETED),
            FOLLOW_CREATED: make_async_handler(process_follow_event, "follows", "New follow", FOLLOW_CREATED),
            FOLLOW_DELETED: make_async_handler(process_follow_event, "follows", "Follow removed", FOLLOW_DELETED),
            FRIEND_ADDED: make_async_handler(process_friend_event, "friends", "New friend", FRIEND_ADDED),
            FRIEND_REMOVED: make_async_handler(process_friend_event, "friends", "Friend removed", FRIEND_REMOVED),
            MESSAGE_EVENT: make_async_handler(process_messenger_event, "messenger", "New message", MESSAGE_EVENT),
            NEWSFEED_CREATED: make_async_handler(process_newsfeed_event, "newsfeed", "Feed item created", NEWSFEED_CREATED),
            NEWSFEED_UPDATED: make_async_handler(process_newsfeed_event, "newsfeed", "Feed updated", NEWSFEED_UPDATED),
            NEWSFEED_DELETED: make_async_handler(process_newsfeed_event, "newsfeed", "Feed removed", NEWSFEED_DELETED),
            REACTION_ADDED: make_async_handler(process_reaction_event, "reactions", "Reaction added", REACTION_ADDED),
            REACTION_CREATED: make_async_handler(process_reaction_event, "reactions", "New reaction", REACTION_CREATED),
            REACTION_UPDATED: make_async_handler(process_reaction_event, "reactions", "Reaction updated", REACTION_UPDATED),
            REACTION_DELETED: make_async_handler(process_reaction_event, "reactions", "Reaction deleted", REACTION_DELETED),
            TAG_ADDED: make_async_handler(process_tagging_event, "tagging", "Tag added", TAG_ADDED),
            TAG_REMOVED: make_async_handler(process_tagging_event, "tagging", "Tag removed", TAG_REMOVED),
            NOTIFICATION_SENT: make_async_handler(create_notification, "notifications", "Notification sent", NOTIFICATION_SENT),
            POST_CREATED: make_async_handler(handle_post_created, "social", "New post created", POST_CREATED),
            POST_UPDATED: make_async_handler(process_social_event, "social", "Post updated", POST_UPDATED),
            POST_DELETED: make_async_handler(process_social_event, "social", "Post deleted", POST_DELETED),
        }

        handlers["post_newsfeed_created"] = make_async_handler(
            process_newsfeed_event, "newsfeed", "Feed item created", "post_newsfeed_created"
        )

        handlers["user_created"] = handlers.get(USER_REGISTERED)

        return handlers

    async def _consume_loop(self):
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

        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            group_id=self.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            max_poll_records=10,
            max_poll_interval_ms=300000,
        )
        await self.consumer.start()
        logger.info(f"Started Kafka consumer on topics: {self.topics}")

        try:
            async for msg in self.consumer:
                close_old_connections()
                raw = msg.value
                if settings.KAFKA_ENCRYPTION_KEY:
                    raw = Fernet(settings.KAFKA_ENCRYPTION_KEY.encode()).decrypt(raw)
                try:
                    payload = json.loads(raw.decode("utf-8"))
                    event = EventData.parse_obj(payload)
                except (ValidationError, json.JSONDecodeError) as e:
                    logger.error(f"Invalid payload: {e}")
                    continue

                data = dict(event.data)
                data["id"] = event.id
                handler = self.handlers.get(event.event_type)
                if handler:
                    await handler(data)
                else:
                    logger.warning(f"No handler for {event.event_type}")
        finally:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    def start(self):
        asyncio.run(self._consume_loop())
