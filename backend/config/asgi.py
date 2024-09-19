import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Ensure that Django is set up before importing routing modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import routing modules from all apps after Django setup
import messenger.routing
import notifications.routing
import comments.routing
import follows.routing
import reactions.routing
import social.routing
import users.routing
import albums.routing
import friends.routing
import newsfeed.routing
import pages.routing
import stories.routing
import tagging.routing

# Combine all WebSocket routing patterns
websocket_urlpatterns = (
    messenger.routing.websocket_urlpatterns +
    notifications.routing.websocket_urlpatterns +
    comments.routing.websocket_urlpatterns +
    follows.routing.websocket_urlpatterns +
    reactions.routing.websocket_urlpatterns +
    social.routing.websocket_urlpatterns +
    users.routing.websocket_urlpatterns +
    albums.routing.websocket_urlpatterns +
    friends.routing.websocket_urlpatterns +
    newsfeed.routing.websocket_urlpatterns +
    pages.routing.websocket_urlpatterns +
    stories.routing.websocket_urlpatterns +
    tagging.routing.websocket_urlpatterns
)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
