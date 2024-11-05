import jwt
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from asgiref.sync import sync_to_async
from jwt import ExpiredSignatureError, DecodeError

User = get_user_model()


class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that takes a JWT token from the query string or headers and authenticates via Django.
    """

    async def __call__(self, scope, receive, send):
        # Get the token from query params or headers
        token = None
        query_string = scope['query_string'].decode()
        params = parse_qs(query_string)

        # Get token from query string
        token = params.get('token', [None])[0]

        if not token:
            # Optionally, you can also allow extracting token from headers.
            headers = dict(scope.get('headers', []))
            if b'authorization' in headers:
                auth_header = headers[b'authorization'].decode().split()
                if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
                    token = auth_header[1]

        if not token:
            # Assign AnonymousUser if token is not found
            scope['user'] = AnonymousUser()
            return await super().__call__(scope, receive, send)

        # Validate the token and get the user
        try:
            # Using SimpleJWT to validate token
            validated_token = UntypedToken(token)

            # Decode token and fetch user ID (could be in the payload, depends on how you structured it)
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get('user_id')

            # Get the user from DB using async to avoid blocking
            user = await sync_to_async(User.objects.get)(id=user_id)
            scope['user'] = user

        except (TokenError, User.DoesNotExist, DecodeError, ExpiredSignatureError,
                InvalidToken) as e:
            # Token is invalid, set user as anonymous
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
