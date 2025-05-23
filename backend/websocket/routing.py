from django.urls import re_path
from .consumers import (
    PostConsumer, AlbumConsumer, CommentConsumer, FollowConsumer,
    FriendConsumer, MessengerConsumer, NewsfeedConsumer,
    ReactionConsumer, SocialConsumer, StoryConsumer,
    TaggingConsumer, NotificationConsumer, UserConsumer, DefaultConsumer,
)

websocket_urlpatterns = [
    re_path(r"^ws/presence/?$", UserConsumer.as_asgi()),

    # —— OTHER CHANNELS ————————————————————————————————————————
    re_path(r"^ws/posts/$",         PostConsumer.as_asgi()),
    re_path(r"^ws/albums/$",        AlbumConsumer.as_asgi()),
    re_path(r"^ws/comments/$",      CommentConsumer.as_asgi()),
    re_path(r"^ws/follows/$",       FollowConsumer.as_asgi()),
    re_path(r"^ws/friends/$",       FriendConsumer.as_asgi()),
    re_path(r"^ws/messenger/$",     MessengerConsumer.as_asgi()),
    re_path(r"^ws/newsfeed/$",      NewsfeedConsumer.as_asgi()),
    re_path(r"^ws/reactions/$",     ReactionConsumer.as_asgi()),
    re_path(r"^ws/social/$",        SocialConsumer.as_asgi()),
    re_path(r"^ws/stories/$",       StoryConsumer.as_asgi()),
    re_path(r"^ws/tagging/$",       TaggingConsumer.as_asgi()),
    re_path(r"^ws/notifications/$", NotificationConsumer.as_asgi()),

    # fallback
    re_path(r'^.*$', DefaultConsumer.as_asgi()),
]
