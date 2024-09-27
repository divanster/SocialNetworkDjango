from django.urls import re_path
from .consumers import TaggingConsumer

websocket_urlpatterns = [
    re_path(r'^ws/tagging/(?P<item_id>[0-9a-f-]+)/$', TaggingConsumer.as_asgi()),
]
