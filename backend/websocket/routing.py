# backend/websocket/routing.py

from django.urls import path
from websocket.consumers import (
    PostConsumer,
    AlbumConsumer,
    CommentConsumer,
    FollowConsumer,
    FriendConsumer,
    MessengerConsumer,
    NewsfeedConsumer,
    ReactionConsumer,
    SocialConsumer,
    StoryConsumer,
    TaggingConsumer,
    UserConsumer,
    NotificationConsumer,
    PresenceConsumer,
    DefaultConsumer,
)

websocket_urlpatterns = [
    path("ws/posts/", PostConsumer.as_asgi()),
    path("ws/albums/", AlbumConsumer.as_asgi()),
    path("ws/comments/", CommentConsumer.as_asgi()),
    path("ws/follows/", FollowConsumer.as_asgi()),
    path("ws/friends/", FriendConsumer.as_asgi()),
    path("ws/messenger/", MessengerConsumer.as_asgi()),
    path("ws/newsfeed/", NewsfeedConsumer.as_asgi()),
    path("ws/reactions/", ReactionConsumer.as_asgi()),
    path("ws/social/", SocialConsumer.as_asgi()),
    path("ws/stories/", StoryConsumer.as_asgi()),
    path("ws/tagging/", TaggingConsumer.as_asgi()),
    path("ws/users/", UserConsumer.as_asgi()),
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    path("ws/presence/", PresenceConsumer.as_asgi()),
    path("ws/", DefaultConsumer.as_asgi()),
    # Add more routes as needed for other appss
]
