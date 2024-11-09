from uuid import UUID

from django.db.models import Q
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Message, Conversation
from .serializers import (MessageSerializer, MessagesCountSerializer,
                          ConversationSerializer)
import logging

logger = logging.getLogger(__name__)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    A viewset for creating, retrieving, and listing conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.participants.add(self.request.user)
        logger.info(f"Conversation created: {instance}")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="pk",
                type=UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the conversation"
            ),
        ],
        responses=ConversationSerializer,
    )
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific conversation by its UUID.
        """
        conversation = self.get_object()
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and deleting Message instances.
    """
    queryset = Message.objects.none()  # Empty queryset for schema generation
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'  # Ensure the correct field is used for lookups
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        # Filter messages that belong to conversations in which the user is a participant
        return Message.objects.filter(
            Q(conversation__participants=user) &
            (Q(deleted_by_sender=False) | Q(deleted_by_receiver=False))
        ).distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="pk",
                type=UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the message"
            ),
        ],
        responses=MessageSerializer,
    )
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific message by its UUID.
        """
        message = self.get_object()
        if not message.is_visible_to(request.user):
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(message)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Overriding the default create method to ensure a valid conversation is used.
        """
        conversation = serializer.validated_data.get('conversation')
        if not conversation:
            return Response(
                {"error": "Conversation must be specified."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not conversation.participants.filter(pk=self.request.user.pk).exists():
            conversation.participants.add(self.request.user)

        instance = serializer.save(sender=self.request.user)
        logger.info(f"Message created: {instance}")

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(f"Message updated: {instance}")

    def perform_destroy(self, instance):
        logger.info(f"Soft deleting message: {instance}")
        instance.mark_as_deleted(self.request.user)


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
        user = request.user
        message_count = Message.objects.filter(
            Q(conversation__participants=user) &
            Q(deleted_by_sender=False) & Q(deleted_by_receiver=False)
        ).count()
        serializer = self.get_serializer({"count": message_count})
        return Response(serializer.data)
