# backend/config/custom_error_middleware.py

import logging
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.http import Http404

logger = logging.getLogger(__name__)

class CustomErrorMiddleware:
    """
    Middleware to handle exceptions and return custom JSON responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Handle PermissionDenied exceptions
        if isinstance(exception, PermissionDenied):
            logger.warning(f"Permission Denied: {exception}")
            return JsonResponse({'error': {'type': 'PermissionDenied',
                                           'message': str(exception)}}, status=403)

        # Handle Http404 exceptions
        elif isinstance(exception, Http404):
            logger.info(f"Resource Not Found: {exception}")
            return JsonResponse({'error': {'type': 'NotFound',
                                           'message': 'The requested resource was not '
                                                      'found'}}, status=404)

        # Handle other exceptions
        else:
            logger.error(f"Unhandled Exception: {exception}", exc_info=True)
            return JsonResponse({'error': {'type': 'ServerError',
                                           'message': 'An unexpected error occurred.'}}, status=500)
