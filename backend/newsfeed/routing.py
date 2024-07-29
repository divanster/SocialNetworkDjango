# backend/newsfeed/routing.py
from django.urls import re_path
from .consumers import NewsfeedConsumer

websocket_urlpatterns = [
    re_path(r'ws/newsfeed/$', NewsfeedConsumer.as_asgi()),
]
