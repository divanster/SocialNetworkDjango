# backend/config/custom_error_middleware.py

import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Log the exception for internal review.
        logger.error(f"Unhandled Exception: {exception}", exc_info=True)

        # Return a JSON response for any unhandled server exceptions
        response_data = {
            "error": {
                "type": "ServerError",
                "message": "An unexpected error occurred. Please try again later.",
            }
        }
        return JsonResponse(response_data, status=500)
