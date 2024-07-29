# backend/pages/routing.py
from django.urls import re_path
from .consumers import PageConsumer

websocket_urlpatterns = [
    re_path(r'ws/pages/$', PageConsumer.as_asgi()),
]
