# backend/core/middleware.py

import logging
from graphql import parse, validate, GraphQLError
from core.graphql_validation import ComplexityLimitRule, DepthLimitRule

logger = logging.getLogger(__name__)


class GraphQLValidationMiddleware:
    """
    Middleware to validate GraphQL queries against custom rules.
    """

    def __init__(self, schema):
        self.schema = schema

    def resolve(self, next, root, info, **args):
        # Access the query from the info
        try:
            query = info.context.request.body.decode('utf-8')
        except AttributeError:
            # info.context.request is not available (e.g., in Celery workers)
            return next(root, info, **args)

        try:
            document = parse(query)
            validation_errors = validate(
                self.schema,
                document,
                rules=[ComplexityLimitRule, DepthLimitRule]
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

        return next(root, info, **args)


class GraphQLLoggingMiddleware:
    """
    Middleware to log GraphQL requests and responses.
    """

    def __init__(self):
        pass

    def resolve(self, next, root, info, **args):
        try:
            request = info.context.request
            logger.info(f"GraphQL Request: {request.method} {request.path}")
            logger.debug(f"Request Body: {request.body.decode('utf-8')}")
        except AttributeError:
            # info.context.request is not available
            pass

        try:
            response = next(root, info, **args)
            try:
                logger.info(f"GraphQL Response Status: {response.status_code}")
                logger.debug(f"Response Data: {response.content.decode('utf-8')}")
            except AttributeError:
                # response may not have these attributes
                pass
            return response
        except Exception as e:
            logger.error(f"GraphQL Error: {str(e)}")
            raise e
