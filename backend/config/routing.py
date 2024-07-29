from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from albums.routing import websocket_urlpatterns as albums_ws
from friends.routing import websocket_urlpatterns as friends_ws
from newsfeed.routing import websocket_urlpatterns as newsfeed_ws
from pages.routing import websocket_urlpatterns as pages_ws
from stories.routing import websocket_urlpatterns as stories_ws

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            albums_ws +
            friends_ws +
            newsfeed_ws +
            pages_ws +
            stories_ws
        )
    ),
})
