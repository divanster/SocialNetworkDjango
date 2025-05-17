# backend/config/routing.py
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

from websocket.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # every pattern in websocket_urlpatterns will be available at /ws/<pattern>
            re_path(r"^ws/", URLRouter(websocket_urlpatterns)),
        ])
    ),
})
