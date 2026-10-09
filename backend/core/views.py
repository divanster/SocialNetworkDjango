import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection

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
def health_check(request):
    payload = {
        "application": "healthy",
        "database": "unknown",
    }

    try:
        connection.ensure_connection()
        payload["database"] = "healthy" if connection.is_usable() else "unhealthy"
    except Exception as e:
        logger.error("DB health error: %s", e)
        payload["database"] = "unhealthy"

    code = 200 if payload["database"] == "healthy" else 503
    return JsonResponse(payload, status=code)
