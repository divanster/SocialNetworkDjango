# core/views.py

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection  # Import for database health check

logger = logging.getLogger('core')


@csrf_exempt  # Disable CSRF protection for this view
@require_http_methods(["POST"])  # Only allow POST requests
def csp_report(request):
    """
    Log CSP reports sent by the browser.
    """
    report_data = json.loads(request.body.decode('utf-8'))
    logger.warning('CSP Violation: %s', json.dumps(report_data, indent=2))
    return JsonResponse({'status': 'ok'}, status=204)


@require_http_methods(["GET"])  # Allow only GET requests
def health_check(request):
    """
    Health check endpoint to ensure the application is running.
    This can be extended to include checks for the database, cache, etc.
    """
    health_status = {
        "application": "healthy",
        "database": "unknown"
    }

    # Check database connectivity
    try:
        connection.ensure_connection()
        if connection.is_usable():
            health_status["database"] = "healthy"
        else:
            health_status["database"] = "unhealthy"
    except Exception as e:
        health_status["database"] = "unhealthy"
        logger.error(f"Database health check failed: {e}")

    status_code = 200 if health_status["database"] == "healthy" else 503

    return JsonResponse(health_status, status=status_code)
