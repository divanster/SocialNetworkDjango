from django.urls import re_path
from kafka_app.consumer import KafkaConsumerApp  # Import centralized Kafka consumer

websocket_urlpatterns = [
    re_path(r'ws/comments/$', KafkaConsumerApp.as_asgi()),  # Update to use centralized consumer
]
