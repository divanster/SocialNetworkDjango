import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Ensure that Django settings are properly set up before importing any routing modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import the centralized WebSocket routing module
from websocket.routing import websocket_urlpatterns  # Updated import to centralized routing

# Define the ASGI application that handles HTTP and WebSocket protocols
application = ProtocolTypeRouter({
    # HTTP requests will be handled using the default Django ASGI application
    "http": get_asgi_application(),

    # WebSocket connections are handled through the centralized WebSocket routing
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Use centralized WebSocket routing
        )
    ),
})
