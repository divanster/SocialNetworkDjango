# backend/core/graphql_views.py

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
    Custom GraphQL view to handle JWT authentication.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context(self, request):
        # Handle JWT Authentication
        auth = JWTAuthentication()
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split()[1]
            except IndexError:
                logger.error("Invalid Authorization header format.")
        elif 'token' in request.GET:
            token = request.GET['token']

        if token:
            try:
                user_auth_tuple = auth.authenticate(request)
                if user_auth_tuple is not None:
                    user, token_obj = user_auth_tuple
                    return {'user': user, 'token': token_obj}
            except (InvalidToken, AuthenticationFailed) as e:
                logger.error(f"Invalid token error: {str(e)}")
        return {'user': AnonymousUser()}
