from django.urls import re_path
from kafka_app.consumer import KafkaConsumerApp

websocket_urlpatterns = [
    re_path(r'^ws/friend-requests/(?P<user_id>\d+)/$', KafkaConsumerApp.as_asgi()),  # Update to use centralized consumer
]
