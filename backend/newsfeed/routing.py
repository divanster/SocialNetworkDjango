# backend/newsfeed/routing.py
from django.urls import re_path
from .consumer import NewsfeedKafkaConsumer

websocket_urlpatterns = [
    re_path(r'ws/newsfeed/$', NewsfeedKafkaConsumer.as_asgi()),
]
