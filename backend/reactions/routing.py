# backend/reactions/routing.py
from django.urls import re_path
from .consumers import ReactionConsumer

websocket_urlpatterns = [
    re_path(r'ws/reactions/$', ReactionConsumer.as_asgi()),
]
