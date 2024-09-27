from django.urls import re_path
from .consumers import StoryConsumer

websocket_urlpatterns = [
    re_path(r'^ws/stories/(?P<user_id>\d+)/$', StoryConsumer.as_asgi()),
]
