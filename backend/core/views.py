import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
import redis
from kafka_app.producer import KafkaProducerClient as KafkaProducer
from django.conf import settings

# Setting up the logger for the core application
logger = logging.getLogger('core')


# ===========================
# CSP Report View
# ===========================
@csrf_exempt
@require_http_methods(["POST"])
def csp_report(request):
    """
    Log CSP reports sent by the browser.
    """
    try:
        report_data = json.loads(request.body.decode('utf-8'))
        logger.warning('CSP Violation: %s', json.dumps(report_data, indent=2))
        return JsonResponse({'status': 'ok'}, status=204)
    except json.JSONDecodeError:
        logger.error('CSP Violation: Unable to parse JSON data.')
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)


# ===========================
# Health Check View
# ===========================
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for DB, Redis, and Kafka.
    """
    health_status = {
        "application": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "kafka": "unknown"
    }

    # Database
    try:
        connection.ensure_connection()
        health_status["database"] = "healthy" if connection.is_usable() else "unhealthy"
    except Exception as e:
        health_status["database"] = "unhealthy"
        logger.error(f"Database health check failed: {e}")

    # Redis
    try:
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        r.ping()
        health_status["redis"] = "healthy"
    except redis.ConnectionError as e:
        health_status["redis"] = "unhealthy"
        logger.error(f"Redis health check failed: {e}")

    # Kafka
    try:
        producer = KafkaProducer()
        producer.flush()
        health_status["kafka"] = "healthy"
    except Exception as e:
        health_status["kafka"] = "unhealthy"
        logger.error(f"Kafka health check failed: {e}")

    status_code = 200 if all(v == "healthy" for v in health_status.values()) else 503
    return JsonResponse(health_status, status=status_code)
