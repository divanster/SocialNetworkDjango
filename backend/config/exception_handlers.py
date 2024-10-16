# backend/config/exception_handlers.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add a custom structure for errors.
    if response is not None:
        custom_response_data = {
            'error': {
                'type': exc.__class__.__name__,
                'message': str(exc),
                'details': response.data
            }
        }
        response.data = custom_response_data
    else:
        # Handle 500 internal server error or any uncaught exceptions.
        custom_response_data = {
            'error': {
                'type': 'ServerError',
                'message': 'An unexpected error occurred.',
                'details': str(exc),
            }
        }
        response = Response(custom_response_data,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
