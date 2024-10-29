from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Notification
from .serializers import NotificationSerializer, NotificationCountSerializer
from django.shortcuts import get_object_or_404


class NotificationViewSet(viewsets.ViewSet):
    """
    A viewset for viewing and editing Notification instances.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Returns a list of notifications for the current user.
        """
        notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns a specific notification by its ID.
        """
        # Get the notification for the current user by id.
        notification = get_object_or_404(Notification, id=pk, receiver=request.user)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_all_as_read(self, request):
        """
        Marks all unread notifications as read for the logged-in user.
        """
        notifications = Notification.objects.filter(receiver=request.user, is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        return Response({"message": f"{count} notifications marked as read."}, status=200)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """
        Marks a specific notification as read.
        """
        notification = get_object_or_404(Notification, id=pk, receiver=request.user)
        notification.mark_as_read()
        return Response({"message": f"Notification {pk} marked as read."}, status=200)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def unread_count(self, request):
        """
        Returns the count of unread notifications.
        """
        count = Notification.objects.filter(receiver=request.user, is_read=False).count()
        return Response({"count": count})


class NotificationsCountView(APIView):
    """
    A view to return the count of unread notifications for a user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get the number of unread notifications for the logged-in user.
        """
        # Query to get the count of unread notifications
        count = Notification.objects.filter(receiver=request.user,
                                            is_read=False).count()

        # Use the serializer to return a consistent response structure
        serializer = NotificationCountSerializer({'count': count})
        return Response(serializer.data)
