from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/comments/(?P<recipe_id>\d+)/$', consumers.CommentConsumer.as_asgi()),
    re_path(r'ws/activity-status/$', consumers.ActivityStatusConsumer.as_asgi()),
]
