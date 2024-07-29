# backend/stories/routing.py
from django.urls import re_path
from .consumers import StoryConsumer

websocket_urlpatterns = [
    re_path(r'ws/stories/$', StoryConsumer.as_asgi()),
]
