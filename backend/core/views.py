import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import redis
from asgiref.sync import sync_to_async
from django.db import connection
from kafka_app.services import KafkaService
from django.conf import settings

logger = logging.getLogger('core')


@csrf_exempt
@require_http_methods(["POST"])
def csp_report(request):
    try:
        data = json.loads(request.body.decode())
        logger.warning('CSP violation: %s', json.dumps(data, indent=2))
        return JsonResponse({}, status=204)
    except json.JSONDecodeError:
        logger.error('CSP report malformed')
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)


@require_http_methods(["GET"])
async def health_check(request):
    status = {
        "application": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "kafka": "unknown",
    }

    # 1) DB health: do both calls on the same sync-to-async thread
    @sync_to_async
    def _check_db():
        connection.ensure_connection()
        return connection.is_usable()

    try:
        db_ok = await _check_db()
        status["database"] = "healthy" if db_ok else "unhealthy"
    except Exception as e:
        logger.error("DB health error: %s", e)
        status["database"] = "unhealthy"

    # 2) Redis health
    try:
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        r.ping()
        status["redis"] = "healthy"
    except Exception as e:
        logger.error("Redis health error: %s", e)
        status["redis"] = "unhealthy"

    # 3) Kafka health
    try:
        client = KafkaService()
        producer = await client._get_producer()
        status["kafka"] = "healthy" if producer is not None else "unhealthy"
    except Exception as e:
        logger.error("Kafka health error: %s", e)
        status["kafka"] = "unhealthy"

    code = 200 if all(v == "healthy" for v in status.values()) else 503
    return JsonResponse(status, status=code)
