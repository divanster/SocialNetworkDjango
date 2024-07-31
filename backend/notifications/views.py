# backend/notifications/views.py
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer, NotificationCountSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class NotificationsCountView(APIView):
    serializer_class = NotificationCountSerializer

    def get(self, request):
        count = Notification.objects.filter(user=request.user, read=False).count()
        return Response({'count': count})
