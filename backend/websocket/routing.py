# backend/websocket/routing.py

from django.urls import re_path
from .consumers import GeneralKafkaConsumer

websocket_urlpatterns = [
    # Route all WebSocket connections dynamically using the group name
    re_path(r'ws/(?P<group_name>\w+)/$', GeneralKafkaConsumer.as_asgi()),
]
