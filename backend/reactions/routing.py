from django.urls import re_path
from .consumers import ReactionConsumer

websocket_urlpatterns = [
    re_path(r'^ws/reactions/(?P<post_id>[0-9a-f-]+)/$', ReactionConsumer.as_asgi()),
]
