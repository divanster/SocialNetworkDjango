from django.urls import re_path
from .consumers import PostConsumer

websocket_urlpatterns = [
    re_path(r'^ws/posts/(?P<post_id>[0-9a-f-]+)/$', PostConsumer.as_asgi()),
]
