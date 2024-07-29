# backend/social/routing.py
from django.urls import re_path
from .consumers import PostConsumer

websocket_urlpatterns = [
    re_path(r'ws/posts/$', PostConsumer.as_asgi()),
]
