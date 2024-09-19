from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/app_name/(?P<param_name>\w+)/$', consumers.TaggingConsumer.as_asgi()),
]
