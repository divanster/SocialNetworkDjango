from uuid import UUID

from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Notification
from .serializers import NotificationSerializer, NotificationCountSerializer
from django.shortcuts import get_object_or_404


class NotificationViewSet(viewsets.GenericViewSet):
    """
    A viewset for viewing and editing Notification instances.
    """
    queryset = Notification.objects.none()  # Added queryset for schema generation
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-created_at')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="pk",
                type=UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the notification"
            ),
        ],
        responses=NotificationSerializer,
    )
    def retrieve(self, request, pk=None):
        """
        Returns a specific notification by its UUID.
        """
        notification = self.get_object()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @extend_schema(
        responses={200: OpenApiResponse(description="All unread notifications marked as read.")}
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_all_as_read(self, request):
        """
        Marks all unread notifications as read for the logged-in user.
        """
        notifications = Notification.objects.filter(receiver=request.user, is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        return Response({"message": f"{count} notifications marked as read."}, status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="pk",
                type=UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the notification"
            ),
        ],
        responses={200: OpenApiResponse(description="Notification marked as read.")}
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """
        Marks a specific notification as read.
        """
        notification = self.get_object()
        notification.mark_as_read()
        return Response({"message": f"Notification {pk} marked as read."}, status=200)

    @extend_schema(
        responses=NotificationCountSerializer
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def unread_count(self, request):
        """
        Returns the count of unread notifications.
        """
        count = Notification.objects.filter(receiver=request.user, is_read=False).count()
        serializer = NotificationCountSerializer({"count": count})
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
        return Response(serializer.data)
