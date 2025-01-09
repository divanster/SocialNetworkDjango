from uuid import UUID

from django.db.models import Q
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Message
from .serializers import MessageSerializer, MessagesCountSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


class MessageViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and deleting Message instances.
    Integrates soft deletion and uses UUIDs as primary keys.
    """
    queryset = Message.objects.none()  # Placeholder for schema generation
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'  # Changed from 'pk' to 'id' for UUID fields
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        """
        Restrict the queryset to messages where the user is either the sender or receiver.
        Excludes soft-deleted messages by default.
        """
        user = self.request.user
        return Message.objects.filter(Q(receiver=user) | Q(sender=user))

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type=UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the message"
            ),
        ],
        responses=MessageSerializer,
    )
    def retrieve(self, request, id=None):
        """
        Retrieve a specific message by its UUID.
        """
        message = self.get_object()
        serializer = self.get_serializer(message)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Automatically set the sender to the authenticated user upon message creation.
        """
        instance = serializer.save(sender=self.request.user)
        logger.info(f"Message created: {instance}")

    def perform_update(self, serializer):
        """
        Update the message instance.
        """
        instance = serializer.save()
        logger.info(f"Message updated: {instance}")

    def perform_destroy(self, instance):
        """
        Soft delete the message instead of hard deleting.
        """
        instance.delete()
        logger.info(f"Message soft-deleted: {instance}")

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, id=None):
        """
        Custom action to mark a message as read.
        """
        message = self.get_object()

        if message.receiver != request.user:
            logger.warning(
                f"User {request.user.id} attempted to mark a message not addressed to them as read.")
            return Response(
                {"detail": "You do not have permission to mark this message as read."},
                status=status.HTTP_403_FORBIDDEN
            )

        if message.is_read:
            logger.info(f"Message {message.id} is already marked as read.")
            return Response(
                {"detail": "Message is already marked as read."},
                status=status.HTTP_200_OK
            )

        try:
            message.mark_as_read()
            logger.info(f"Message {message.id} marked as read.")
            return Response(
                {"detail": "Message marked as read."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MessagesCountView(generics.GenericAPIView):
    """
    API View for getting the count of messages related to the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessagesCountSerializer

    @extend_schema(
        responses=MessagesCountSerializer
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve the count of messages where the user is either sender or receiver.
        Excludes soft-deleted messages.
        """
        user = request.user
        message_count = Message.objects.filter(
            Q(receiver=user) | Q(sender=user)).count()
        serializer = self.get_serializer({"count": message_count})
        return Response(serializer.data)
