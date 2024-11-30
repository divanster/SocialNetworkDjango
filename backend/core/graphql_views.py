from graphene_django.views import GraphQLView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)


class CustomGraphQLView(GraphQLView):
    """
    Custom GraphQL view to handle JWT authentication for GraphQL queries.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def parse_body(self, request):
        """
        Attempt to authenticate the request using JWT tokens.
        If token is present and valid, set the user in the request context.
        """
        auth = JWTAuthentication()

        # Check for Authorization header or query params
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[
                1]  # Extract token from 'Bearer token' format
        elif 'token' in request.GET:
            token = request.GET['token']

        if not token:
            request.user = AnonymousUser()
            return super().parse_body(request)

        try:
            # Validate the token
            user_auth_tuple = auth.authenticate(request)
            if user_auth_tuple is not None:
                request.user, request.token = user_auth_tuple
            else:
                request.user = AnonymousUser()
        except (InvalidToken, AuthenticationFailed) as e:
            logger.error(f"Invalid token error: {str(e)}")
            request.user = AnonymousUser()

        return super().parse_body(request)
