# backend/albums/consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from albums.models import Album
from django.core.cache import cache

User = get_user_model()
logger = logging.getLogger(__name__)

class AlbumConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            logger.warning("[WebSocket] Unauthorized access attempt.")
            return

        self.user = self.scope["user"]
        self.room_group_name = 'albums'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"[WebSocket] User {self.user.id} connected to albums group.")
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"[WebSocket] User {self.user.id} disconnected from albums group.")

    async def album_message(self, event):
        tagged_user_ids = event.get('tagged_user_ids', [])
        tagged_users = await self.get_users(tagged_user_ids)

        await self.send(text_data=json.dumps({
            'event': event['event'],
            'album': str(event['album']),
            'title': event['title'],
            'description': event['description'],
            'tagged_users': tagged_users,
        }))

    @database_sync_to_async
    def get_users(self, user_ids):
        cached_users = cache.get_many(user_ids)
        missing_ids = [uid for uid in user_ids if uid not in cached_users]

        # Fetch users only if not already cached
        if missing_ids:
            missing_users = User.objects.filter(id__in=missing_ids).using('default').values('id', 'username')
            # Add to cache with a timeout
            cache.set_many({user['id']: user for user in missing_users}, timeout=300)
            cached_users.update({user['id']: user for user in missing_users})

        return list(cached_users.values())
