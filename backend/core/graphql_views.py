# backend/core/graphql_views.py

from graphene_django.views import GraphQLView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from graphql import parse, validate, GraphQLError
from core.graphql_validation import ComplexityLimitRule, DepthLimitRule
import logging
import json  # Import JSON module

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
        Authenticate the request using JWT tokens.
        """
        auth = JWTAuthentication()

        # Extract token from Authorization header or query parameters
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
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

    def execute_graphql_request(self, *args, **kwargs):
        """
        Override to add custom validation and logging.
        """
        request = self.request
        logger.info(f"GraphQL Request: {request.method} {request.path}")
        try:
            # Parse the JSON body
            body_unicode = request.body.decode('utf-8') if request.body else ''
            body = json.loads(body_unicode) if body_unicode else {}
            query = body.get('query', '')
            variables = body.get('variables', {})
            operation_name = body.get('operationName')

            logger.debug(f"Query: {query}")
            logger.debug(f"Variables: {variables}")

            # Validate the query
            try:
                document = parse(query)
                # Pass the underlying GraphQLSchema to validate
                validation_errors = validate(
                    self.schema.graphql_schema,  # Access the underlying GraphQLSchema
                    document,
                    rules=[ComplexityLimitRule, DepthLimitRule]  # Pass classes, not instances
                )
                if validation_errors:
                    error_messages = [error.message for error in validation_errors]
                    raise GraphQLError(", ".join(error_messages))
            except GraphQLError as e:
                logger.error(f"GraphQL Validation Error: {str(e)}")
                raise e
            except Exception as e:
                logger.error(f"Unexpected Validation Error: {str(e)}")
                raise e

            # Execute the request
            response = super().execute_graphql_request(*args, **kwargs)

            # Log the response
            if hasattr(response, 'status_code') and hasattr(response, 'content'):
                logger.info(f"GraphQL Response Status: {response.status_code}")
                try:
                    logger.debug(f"Response Data: {response.content.decode('utf-8')}")
                except UnicodeDecodeError:
                    logger.debug("Response Data: [Binary Data]")
            else:
                logger.debug(f"Response Data: {response}")

            return response

        except Exception as e:
            logger.error(f"GraphQL Execution Error: {str(e)}")
            raise e
