# backend/core/views.py

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
import redis
from kafka import KafkaProducer
from django.conf import settings

# Setting up the logger for the core application
logger = logging.getLogger('core')


# ===========================
# CSP Report View
# ===========================

@csrf_exempt  # Disable CSRF protection for this view
@require_http_methods(["POST"])  # Only allow POST requests
def csp_report(request):
    """
    Log CSP reports sent by the browser.

    Content Security Policy (CSP) violations can be reported automatically by the browser to this endpoint.
    The `csp_report` view logs these violations to assist in identifying unexpected script, style, or other
    security-related issues.
    """
    try:
        # Parse the incoming request body, which is in JSON format
        report_data = json.loads(request.body.decode('utf-8'))

        # Log the CSP violation for further analysis
        logger.warning('CSP Violation: %s', json.dumps(report_data, indent=2))

        # Return a successful status response
        return JsonResponse({'status': 'ok'}, status=204)
    except json.JSONDecodeError:
        # If the request body is not valid JSON, log the error and return a 400 Bad
        # Request response
        logger.error('CSP Violation: Unable to parse JSON data.')
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)


# ===========================
# Health Check View
# ===========================

@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint to ensure the application is running correctly.
    This can be extended to include checks for the database, cache, Kafka, etc.
    """
    health_status = {
        "application": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "kafka": "unknown"
    }

    # Check database health
    try:
        connection.ensure_connection()
        health_status["database"] = "healthy" if connection.is_usable() else "unhealthy"
    except Exception as e:
        health_status["database"] = "unhealthy"
        logger.error(f"Database health check failed: {e}")

    # Check Redis health
    try:
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        r.ping()
        health_status["redis"] = "healthy"
    except redis.ConnectionError as e:
        health_status["redis"] = "unhealthy"
        logger.error(f"Redis health check failed: {e}")

    # Check Kafka health
    try:
        # Attempt to connect to Kafka by instantiating a producer
        producer = KafkaProducer(bootstrap_servers=settings.KAFKA_BROKER_URL)
        health_status["kafka"] = "healthy"
    except Exception as e:
        health_status["kafka"] = "unhealthy"
        logger.error(f"Kafka health check failed: {e}")

    # Determine overall health based on the individual services
    status_code = 200 if all(v == "healthy" for v in health_status.values()) else 503

    return JsonResponse(health_status, status=status_code)
