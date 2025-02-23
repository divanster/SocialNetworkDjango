from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Parse query string using urllib.parse.parse_qs
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)  # Correct parsing

        # Extract token from query params or headers
        token = query_params.get("token", [None])[0]  # Token from query string

        # Fallback to Authorization header if token is not in query string
        if not token:
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]  # Extract token after "Bearer"

        # If no token is found, reject the connection
        if not token:
            logger.warning("WebSocket connection rejected: No token provided.")
            await send({"type": "websocket.close", "code": 4000})
            return

        try:
            # Validate the JWT token
            access_token = AccessToken(token)
            user_id = access_token.payload.get(
                "user_id")  # Extract user_id from payload
            scope["user"] = await self.get_user(user_id)  # Attach user to the scope
        except (InvalidToken, TokenError) as e:
            logger.error(f"WebSocket JWT validation failed: {str(e)}")
            await send(
                {"type": "websocket.close", "code": 4000})  # Close connection on error
            return

        return await super().__call__(scope, receive, send)

    async def get_user(self, user_id):
        """
        Fetch the user based on user_id asynchronously.
        If the user does not exist, return an AnonymousUser.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return await User.objects.aget(id=user_id)  # Asynchronously get the user
        except User.DoesNotExist:
            return AnonymousUser()  # Return an anonymous user if not found
