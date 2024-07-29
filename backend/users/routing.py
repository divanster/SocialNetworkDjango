# users/routing.py
from django.urls import path
from .consumers import UserConsumer

websocket_urlpatterns = [
    path('ws/users/', UserConsumer.as_asgi()),
]
