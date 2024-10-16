# backend/config/views.py

from django.http import JsonResponse


def custom_400_view(request, exception=None):
    return JsonResponse({'error': {'type': 'BadRequest', 'message': 'Invalid request'}},
                        status=400)


def custom_403_view(request, exception=None):
    return JsonResponse(
        {'error': {'type': 'PermissionDenied', 'message': 'Permission Denied'}},
        status=403)


def custom_404_view(request, exception=None):
    return JsonResponse({'error': {'type': 'NotFound',
                                   'message': 'The requested resource was not found'}},
                        status=404)


def custom_500_view(request):
    return JsonResponse({'error': {'type': 'ServerError',
                                   'message': 'An internal server error occurred'}},
                        status=500)
