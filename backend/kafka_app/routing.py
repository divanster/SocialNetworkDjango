# kafka_app/routing.py

from django.urls import re_path
from .consumers import GroupConsumer

websocket_urlpatterns = [
    re_path(r'ws/(?P<group_name>\w+)/$', GroupConsumer.as_asgi()),
]
