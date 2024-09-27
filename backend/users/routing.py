from django.urls import re_path
from users.consumers import UserConsumer

websocket_urlpatterns = [
    re_path(r'^ws/users/(?P<user_id>\d+)/$', UserConsumer.as_asgi()),
]
