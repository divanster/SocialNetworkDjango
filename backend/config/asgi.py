# asgi.py

import os
import django
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from websocket.routing import websocket_urlpatterns
from config.middleware import JWTMiddleware

logger = logging.getLogger(__name__)

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})

logger.info("ASGI application loaded")
