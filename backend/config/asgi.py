# backend/config/asgi.py

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import logging

# Set up the Django settings environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django
django.setup()

# Import the centralized WebSocket routing module
from websocket.routing import websocket_urlpatterns  # Central WebSocket routing

# Configure logging for tracking ASGI events and debugging
logger = logging.getLogger(__name__)

# Define the ASGI application that handles HTTP and WebSocket protocols
application = ProtocolTypeRouter({
    # HTTP requests will be handled using the default Django ASGI application
    "http": get_asgi_application(),

    # WebSocket connections are handled through the centralized WebSocket routing
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Include all WebSocket routes
        )
    ),
})

logger.info("ASGI application setup completed successfully.")
