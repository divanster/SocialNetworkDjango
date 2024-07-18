# notifications/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter


@extend_schema(parameters=[OpenApiParameter(name='id', description='ID of the notification', required=True, type=int,
                                            location=OpenApiParameter.PATH)])
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(recipient=user)
