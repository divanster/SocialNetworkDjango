# albums/routing.py
from django.urls import re_path
from kafka_app.consumer import KafkaConsumerApp
websocket_urlpatterns = [
    # Route with post_id
    re_path(r'^ws/posts/(?P<post_id>[0-9a-f-]+)/$', KafkaConsumerApp.as_asgi()),

    # Route without post_id
    re_path(r'^ws/posts/$', KafkaConsumerApp.as_asgi()),
]
