# core/views.py

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

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
