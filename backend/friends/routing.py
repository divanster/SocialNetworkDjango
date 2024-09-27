from django.urls import re_path
from .consumers import FriendRequestConsumer

websocket_urlpatterns = [
    re_path(r'^ws/friend-requests/(?P<user_id>\d+)/$', FriendRequestConsumer.as_asgi()),
]
