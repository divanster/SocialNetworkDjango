# backend/config/asgi.py

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import logging

# Set up the Django settings environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Set up Django for Channels and other services
django.setup()

# Import the centralized WebSocket routing module
from websocket.routing import websocket_urlpatterns  # Updated import for centralized routing
from websocket.middleware import TokenAuthMiddleware  # Import custom middleware

# Configure logging for tracking ASGI events and debugging
logger = logging.getLogger(__name__)

# Define the ASGI application that handles HTTP and WebSocket protocols
application = ProtocolTypeRouter({
    # HTTP requests will be handled using the default Django ASGI application
    "http": get_asgi_application(),

    # WebSocket connections are handled through the centralized WebSocket routing
    "websocket": TokenAuthMiddleware(
        URLRouter(
            websocket_urlpatterns  # Use centralized WebSocket routing from `websocket.routing`
        )
    ),
})

logger.info("ASGI application setup completed successfully.")
