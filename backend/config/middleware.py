# backend/config/middleware.py
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
import logging

logger = logging.getLogger(__name__)
User   = get_user_model()


class JWTMiddleware(BaseMiddleware):
    """
    Authenticates WebSocket requests via

      • ?token=<JWT>         (query string)
      • Authorization: Bearer <JWT> (header)

    Closes the socket with code 4000 if the token is missing or invalid.
    """

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":                # let HTTP pass straight through
            return await super().__call__(scope, receive, send)

        token = self._extract_token(scope)
        if not token:
            logger.warning("WS rejected – no token provided")
            await send({"type": "websocket.close", "code": 4000})
            return

        try:
            payload      = AccessToken(token).payload   # validates & decodes
            scope["user"] = await self._get_user(payload.get("user_id"))
            return await super().__call__(scope, receive, send)

        except TokenError as exc:                       # expired / invalid / black‑listed
            logger.error(f"WS JWT failed: {exc}")
            await send({"type": "websocket.close", "code": 4000})

    # ------------------------------------------------------------------

    def _extract_token(self, scope):
        # 1. query‑string
        qs_token = parse_qs(scope.get("query_string", b"").decode()).get("token", [None])[0]
        if qs_token:
            return qs_token

        # 2. Authorization header
        headers = dict(scope.get("headers", []))
        auth    = headers.get(b"authorization", b"").decode()
        if auth.lower().startswith("bearer "):
            return auth.split(" ", 1)[1]

        return None

    # ------------------------------------------------------------------

    async def _get_user(self, user_id):
        if not user_id:
            return AnonymousUser()
        try:
            return await User.objects.aget(id=user_id)  # async lookup (Django 4.1+)
        except User.DoesNotExist:
            return AnonymousUser()

