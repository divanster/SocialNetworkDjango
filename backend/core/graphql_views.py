# backend/core/graphql_views.py

import json
import logging

from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from graphql import parse, validate
from graphene_django.views import GraphQLView

from core.graphql_validation import ComplexityLimitRule, DepthLimitRule

logger = logging.getLogger(__name__)


class CustomGraphQLView(GraphQLView):
    """
    Custom GraphQL view to handle JWT authentication, query validation, and logging.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def parse_body(self, request):
        """
        Authenticate the request using JWT tokens and return the parsed body.
        """
        auth = JWTAuthentication()

        # Try to extract token from the Authorization header or query parameters
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
            else:
                logger.warning("Authorization header is malformed.")
        elif 'token' in request.GET:
            token = request.GET.get('token')

        # If no token is provided, set the user as AnonymousUser
        if not token:
            logger.info("No token provided; setting request.user to AnonymousUser")
            request.user = AnonymousUser()
            return super().parse_body(request)

        # Attempt to authenticate using the provided token
        try:
            user_auth_tuple = auth.authenticate(request)
            if user_auth_tuple is not None:
                request.user, request.token = user_auth_tuple
                logger.info(f"Authenticated user: {request.user}")
            else:
                logger.warning("JWTAuthentication returned None; setting request.user to AnonymousUser")
                request.user = AnonymousUser()
        except (InvalidToken, AuthenticationFailed) as e:
            logger.error(f"Invalid token error: {str(e)}")
            request.user = AnonymousUser()

        return super().parse_body(request)

    def execute_graphql_request(self, *args, **kwargs):
        """
        Override to add custom query validation and detailed logging.
        """
        request = self.request
        logger.info(f"GraphQL Request: {request.method} {request.path}")

        if request.method != "POST":
            return super().execute_graphql_request(*args, **kwargs)

        body_unicode = request.body.decode('utf-8') if request.body else ''
        try:
            body = json.loads(body_unicode) if body_unicode else {}
        except json.JSONDecodeError:
            return super().execute_graphql_request(*args, **kwargs)

        query = body.get('query', '')
        variables = body.get('variables', {})
        operation_name = body.get('operationName')

        logger.debug(f"Query: {query}")
        logger.debug(f"Variables: {variables}")
        logger.debug(f"Operation Name: {operation_name}")

        if query and settings.ENABLE_GRAPHQL_VALIDATION:
            try:
                document = parse(query)
                validation_errors = validate(
                    self.schema.graphql_schema,  # Access the underlying GraphQLSchema
                    document,
                    rules=[ComplexityLimitRule, DepthLimitRule]  # Pass rule classes (they will be instantiated internally)
                )
                if validation_errors:
                    error_messages = [error.message for error in validation_errors]
                    error_text = ", ".join(error_messages)
                    logger.warning(f"GraphQL Validation Error: {error_text}")
            except Exception as e:
                logger.warning(f"Skipping custom GraphQL validation due to parsing error: {str(e)}")

        return super().execute_graphql_request(*args, **kwargs)
