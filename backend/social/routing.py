# albums/routing.py
from django.urls import re_path
from .consumers import PostConsumer, AllPostsConsumer

websocket_urlpatterns = [
    # Route with post_id
    re_path(r'^ws/posts/(?P<post_id>[0-9a-f-]+)/$', PostConsumer.as_asgi()),

    # Route without post_id
    re_path(r'^ws/posts/$', AllPostsConsumer.as_asgi()),
]
