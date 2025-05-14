# backend/config/middleware.py
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class JWTMiddleware(BaseMiddleware):
    """
    Authenticates WebSocket requests via ?token=... or Authorization header.
    Closes with code 4000 if missing/invalid.
    """

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            # Let HTTP pass through unchanged
            return await super().__call__(scope, receive, send)

        token = self._extract_token(scope)
        if not token:
            logger.warning("WS rejected – no token provided")
            await send({"type": "websocket.close", "code": 4000})
            return  # <-- previously omitted

        try:
            # Validate & decode
            payload = AccessToken(token).payload
            scope["user"] = await self._get_user(payload.get("user_id"))
            # Hand off to next middleware/consumer
            return await super().__call__(scope, receive, send)

        except TokenError as exc:
            logger.error(f"WS JWT failed: {exc}")
            await send({"type": "websocket.close", "code": 4000})
            return  # <-- make sure we don’t fall through

    def _extract_token(self, scope):
        # 1. Try query string
        qs = parse_qs(scope.get("query_string", b"").decode())
        token = qs.get("token", [None])[0]
        if token:
            return token

        # 2. Try Authorization header
        headers = dict(scope.get("headers", []))
        auth = headers.get(b"authorization", b"").decode()
        if auth.lower().startswith("bearer "):
            return auth.split(" ", 1)[1]

        return None

    async def _get_user(self, user_id):
        if not user_id:
            return AnonymousUser()
        try:
            # async ORM lookup
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
