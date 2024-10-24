from django.urls import re_path
from kafka_app.consumer import KafkaConsumerApp  # Correct import

websocket_urlpatterns = [
    re_path(r'ws/albums/$', KafkaConsumerApp.as_asgi()),  # If you need WebSocket, use KafkaConsumerApp or a relevant centralized consumer handler.
]
