# backend/follows/routing.py
from django.urls import re_path
from .consumers import FollowConsumer

websocket_urlpatterns = [
    re_path(r'ws/follows/$', FollowConsumer.as_asgi()),
]
