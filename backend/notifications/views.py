# backend/notifications/views.py

from uuid import UUID

from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Notification
from .serializers import NotificationSerializer, NotificationCountSerializer
from rest_framework.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Notification instances.
    Implements soft deletion and uses UUIDs as primary keys.
    """
    queryset = Notification.objects.none()  # Placeholder for schema generation
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'  # Changed from 'pk' to 'id' for UUID fields
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        """
        Restrict the queryset to notifications where the user is the receiver.
        Excludes soft-deleted notifications by default.
        """
        user = self.request.user
        return Notification.objects.filter(receiver=user).order_by('-created_at')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type=UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the notification"
            ),
        ],
        responses=NotificationSerializer,
    )
    def retrieve(self, request, id=None):
        """
        Retrieve a specific notification by its UUID.
        """
        notification = self.get_object()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @extend_schema(
        responses={200: OpenApiResponse(
            description="All unread notifications marked as read.")}
    )
    @action(detail=False, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def mark_all_as_read(self, request):
        """
        Marks all unread notifications as read for the logged-in user.
        """
        notifications = Notification.objects.filter(receiver=request.user,
                                                    is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        logger.info(
            f"{count} notifications marked as read for user {request.user.username}.")
        return Response({"message": f"{count} notifications marked as read."},
                        status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type=UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the notification"
            ),
        ],
        responses={200: OpenApiResponse(description="Notification marked as read.")}
    )
    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, id=None):
        """
        Marks a specific notification as read.
        """
        notification = self.get_object()

        if notification.receiver != request.user:
            logger.warning(
                f"User {request.user.id} attempted to mark a notification not addressed to them as read.")
            raise PermissionDenied(
                "You do not have permission to mark this notification as read.")

        if notification.is_read:
            logger.info(f"Notification {notification.id} is already marked as read.")
            return Response(
                {"message": "Notification is already marked as read."},
                status=status.HTTP_200_OK
            )

        try:
            notification.mark_as_read()
            logger.info(
                f"Notification {notification.id} marked as read by user {request.user.username}.")
            return Response(
                {"message": f"Notification {id} marked as read."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return Response(
                {"message": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        responses=NotificationCountSerializer
    )
    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def unread_count(self, request):
        """
        Returns the count of unread notifications.
        """
        count = Notification.objects.filter(receiver=request.user,
                                            is_read=False).count()
        serializer = NotificationCountSerializer({"count": count})
        logger.info(f"User {request.user.username} has {count} unread notifications.")
        return Response(serializer.data)


class NotificationsCountView(generics.GenericAPIView):
    """
    A simple API View to get the count of unread notifications for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationCountSerializer

    @extend_schema(
        responses=NotificationCountSerializer
    )
    def get(self, request, *args, **kwargs):
        """
        Returns the count of unread notifications.
        """
        user = request.user
        unread_count = Notification.objects.filter(receiver=user, is_read=False).count()
        serializer = self.get_serializer({"count": unread_count})
        logger.info(f"User {user.username} has {unread_count} unread notifications.")
        return Response(serializer.data, status=status.HTTP_200_OK)
