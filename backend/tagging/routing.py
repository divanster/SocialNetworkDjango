from django.urls import re_path
from kafka_app.consumer import KafkaConsumerApp

websocket_urlpatterns = [
    re_path(r'^ws/tagging/(?P<item_id>[0-9a-f-]+)/$', KafkaConsumerApp.as_asgi()),
]
