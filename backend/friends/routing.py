# backend/friends/routing.py
from django.urls import re_path
from .consumers import FriendRequestConsumer

websocket_urlpatterns = [
    re_path(r'ws/friend-requests/$', FriendRequestConsumer.as_asgi()),
]
