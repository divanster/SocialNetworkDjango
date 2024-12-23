# backend/websocket/middleware.py

from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from asgiref.sync import sync_to_async
import jwt
from jwt import ExpiredSignatureError, DecodeError
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that takes a JWT token from the query string or headers and authenticates via Django.
    """

    async def __call__(self, scope, receive, send):
        # Extract token from query parameters or headers
        token = None
        query_string = scope['query_string'].decode()
        params = parse_qs(query_string)

        # Try to get the token from query string
        token = params.get('token', [None])[0]

        if not token:
            # If no token in query string, try extracting it from the headers
            headers = dict(scope.get('headers', []))
            if b'authorization' in headers:
                auth_header = headers[b'authorization'].decode().split()
                if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
                    token = auth_header[1]

        # If no token is found, assign AnonymousUser
        if not token:
            scope['user'] = AnonymousUser()
            logger.warning("WebSocket connection attempt without token")
            return await super().__call__(scope, receive, send)

        # Validate the token and get the user
        try:
            # Validate JWT Token using SimpleJWT's UntypedToken
            validated_token = UntypedToken(token)  # Validate JWT structure

            # Decode the token to get user details
            decoded_data = jwt.decode(
                token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']],
                options={'verify_exp': True}
            )
            user_id = decoded_data.get(settings.SIMPLE_JWT['USER_ID_CLAIM'])

            if not user_id:
                raise TokenError("Token does not contain user_id.")

            # Retrieve the user asynchronously
            user = await sync_to_async(User.objects.get)(id=user_id)
            scope['user'] = user
            logger.info(f"Authenticated WebSocket connection for user: {user.username}")

        except (TokenError, DecodeError, ExpiredSignatureError, InvalidToken,
                User.DoesNotExist) as e:
            # Token is invalid or expired, set the user as AnonymousUser
            scope['user'] = AnonymousUser()
            logger.warning(f"WebSocket connection attempt with invalid token: {e}")

        return await super().__call__(scope, receive, send)
