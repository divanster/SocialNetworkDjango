# backend/messenger/views.py

from uuid import UUID
from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, permissions, generics, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from friends.models import Block
from .models import Message
from .serializers import MessageSerializer, MessagesCountSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

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
        return Message.objects.filter(Q(receiver=user) | Q(sender=user)).order_by('-created_at')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.UUID,
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

    @extend_schema(
        responses={200: MessageSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def inbox(self, request):
        """
        Custom action to retrieve inbox messages (received messages only).
        """
        user = request.user
        inbox_messages = Message.objects.filter(receiver=user).order_by('-created_at')
        serializer = self.get_serializer(inbox_messages, many=True)
        return Response(serializer.data)

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

    @extend_schema(
        request=serializers.Serializer,  # Define a custom serializer if needed
        responses={201: MessageSerializer(many=True)},
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def broadcast(self, request):
        """
        Custom action to broadcast a message to all users.
        """
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required.'}, status=status.HTTP_400_BAD_REQUEST)

        sender = request.user
        receivers = User.objects.all().exclude(id=sender.id)
        messages = []

        try:
            with transaction.atomic():
                for receiver in receivers:
                    # Check if sender has blocked receiver or vice versa
                    if Block.objects.filter(blocker=sender, blocked=receiver).exists() or \
                       Block.objects.filter(blocker=receiver, blocked=sender).exists():
                        logger.info(f"Skipping message to {receiver.username} due to block.")
                        continue

                    msg = Message.objects.create(sender=sender, receiver=receiver, content=content)
                    messages.append(msg)

            serializer = self.get_serializer(messages, many=True)
            logger.info(f"Broadcast message sent by {sender.username} to {len(messages)} users.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error during broadcast: {e}")
            return Response({'error': 'An unexpected error occurred during broadcast.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        message_count = Message.objects.filter(Q(receiver=user) | Q(sender=user)).count()
        serializer = self.get_serializer({"count": message_count})
        logger.info(f"User {user.username} has {message_count} messages.")
        return Response(serializer.data, status=status.HTTP_200_OK)
