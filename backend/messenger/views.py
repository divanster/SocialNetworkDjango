from uuid import UUID

from django.db.models import Q
from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Message
from .serializers import MessageSerializer, MessagesCountSerializer
import logging

logger = logging.getLogger(__name__)

class MessageViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and deleting Message instances.
    """
    queryset = Message.objects.none()  # Added queryset for schema generation
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'  # Ensures the correct field is used for lookups
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(receiver=user) | Q(sender=user))

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
        serializer = self.get_serializer(message)
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save(sender=self.request.user)
        logger.info(f"Message created: {instance}")

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(f"Message updated: {instance}")

    def perform_destroy(self, instance):
        logger.info(f"Deleting message (soft delete): {instance}")
        instance.delete()


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
        message_count = Message.objects.filter(Q(receiver=user) | Q(sender=user)).count()
        serializer = self.get_serializer({"count": message_count})
        return Response(serializer.data)
