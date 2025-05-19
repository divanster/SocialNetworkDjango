# backend/websocket/routing.py
from django.urls import re_path
from .consumers import (
    PostConsumer, AlbumConsumer, CommentConsumer, FollowConsumer,
    FriendConsumer, MessengerConsumer, NewsfeedConsumer,
    ReactionConsumer, SocialConsumer, StoryConsumer,
    TaggingConsumer, NotificationConsumer, UserConsumer,
    PresenceConsumer, DefaultConsumer,
)

websocket_urlpatterns = [
    re_path(r"^.*$", DefaultConsumer.as_asgi()),
    re_path(r"^posts/$",        PostConsumer.as_asgi()),
    re_path(r"^albums/$",       AlbumConsumer.as_asgi()),
    re_path(r"^comments/$",     CommentConsumer.as_asgi()),
    re_path(r"^follows/$",      FollowConsumer.as_asgi()),
    re_path(r"^friends/$",      FriendConsumer.as_asgi()),
    re_path(r"^messenger/$",    MessengerConsumer.as_asgi()),
    re_path(r"^newsfeed/$",     NewsfeedConsumer.as_asgi()),
    re_path(r"^reactions/$",    ReactionConsumer.as_asgi()),
    re_path(r"^social/$",       SocialConsumer.as_asgi()),
    re_path(r"^stories/$",      StoryConsumer.as_asgi()),
    re_path(r"^tagging/$",      TaggingConsumer.as_asgi()),
    re_path(r"^notifications/", NotificationConsumer.as_asgi()),
    re_path(r"^users/$",        UserConsumer.as_asgi()),
    re_path(r"^presence/$",     PresenceConsumer.as_asgi()),
    # fallback (if you really need it)
    re_path(r"^$",              DefaultConsumer.as_asgi()),
]
