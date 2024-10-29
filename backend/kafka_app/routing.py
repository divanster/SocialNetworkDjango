from django.urls import re_path
from .consumer import KafkaConsumerApp

# Using the centralized Kafka consumer for WebSocket handling
websocket_urlpatterns = [
    re_path(r'ws/kafka_app/$', KafkaConsumerApp.as_asgi()),
]
