# backend/config/graphql_views.py

from graphene_django.views import GraphQLView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
import logging

from core.graphql_validation import DepthLimitRule  # Import your DepthLimitRule
from graphql.validation import specified_rules  # Import default validation rules

logger = logging.getLogger(__name__)


class CustomGraphQLView(GraphQLView):
    """
    Custom GraphQL view to handle JWT authentication and depth limiting.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_validation_rules(self, request):
        """
        Override the method to include custom validation rules.
        """
        # Combine default validation rules with the custom DepthLimitRule
        return specified_rules + (DepthLimitRule,)

    def parse_body(self, request):
        """
        Attempt to authenticate the request using JWT tokens.
        If token is present and valid, set the user in the request context.
        """
        auth = JWTAuthentication()

        # Check for Authorization header or query params
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split()[
                    1]  # Extract token from 'Bearer token' format
            except IndexError:
                logger.error("Invalid Authorization header format.")
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

    def execute_graphql_request(self, request, data, view_kwargs):
        logger.info(f"GraphQL Request Data: {data}")
        response = super().execute_graphql_request(request, data, view_kwargs)
        logger.info(f"GraphQL Response Status: {response.status_code}")
        return response
