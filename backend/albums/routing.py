# backend/albums/routing.py
from django.urls import re_path
from .consumers import AlbumConsumer

websocket_urlpatterns = [
    re_path(r'ws/albums/$', AlbumConsumer.as_asgi()),
]
