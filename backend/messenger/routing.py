from django.urls import re_path
from kafka_app.consumer import KafkaConsumerApp

websocket_urlpatterns = [
    re_path(r'ws/messenger/(?P<room_name>\w+)/$', KafkaConsumerApp.as_asgi()),
    re_path(r'ws/notifications/$', KafkaConsumerApp.as_asgi()),
    re_path(r'ws/activity-status/$', KafkaConsumerApp.as_asgi()),
    re_path(r'ws/comments/$', KafkaConsumerApp.as_asgi()),
]
