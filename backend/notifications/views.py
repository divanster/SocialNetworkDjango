# backend/notifications/views.py

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Notification
from .serializers import NotificationSerializer, NotificationCountSerializer
from django.shortcuts import get_object_or_404
from mongoengine.queryset.visitor import Q


class NotificationViewSet(viewsets.ViewSet):
    """
    A viewset for viewing and editing Notification instances.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Returns a list of notifications for the current user.
        """
        notifications = Notification.objects.filter(receiver_id=request.user.id).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns a specific notification by its ID.
        """
        notification = get_object_or_404(Notification, id=pk, receiver_id=request.user.id)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_all_as_read(self, request):
        """
        Marks all unread notifications as read for the logged-in user.
        """
        notifications = Notification.objects.filter(receiver_id=request.user.id, is_read=False)
        count = notifications.count()
        for notification in notifications:
            notification.mark_as_read()
        return Response({"message": f"{count} notifications marked as read."}, status=200)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """
        Marks a specific notification as read.
        """
        notification = get_object_or_404(Notification, id=pk, receiver_id=request.user.id)
        notification.mark_as_read()
        return Response({"message": f"Notification {pk} marked as read."}, status=200)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def unread_count(self, request):
        """
        Returns the count of unread notifications.
        """
        count = Notification.objects.filter(receiver_id=request.user.id, is_read=False).count()
        return Response({"count": count})


class NotificationsCountView(APIView):
    """
    A view to return the count of unread notifications for a user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationCountSerializer

    def get(self, request):
        """
        Get the number of unread notifications for the logged-in user.
        """
        count = Notification.objects.filter(receiver_id=request.user.id, is_read=False).count()
        return Response({'count': count})
