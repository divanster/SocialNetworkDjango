from django.db.models import Q
from rest_framework import viewsets, permissions, views, response
from rest_framework.exceptions import PermissionDenied
from .models import Message
from .serializers import MessageSerializer
import logging

logger = logging.getLogger(__name__)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Fetch all messages involving the authenticated user
        return Message.objects.filter(Q(receiver=user) | Q(sender=user))

    def perform_create(self, serializer):
        # Automatically set the sender to the currently authenticated user
        instance = serializer.save(sender=self.request.user)
        logger.info(f"Message created: {instance}")

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(f"Message updated: {instance}")

    def perform_destroy(self, instance):
        logger.info(f"Deleting message (soft delete): {instance}")
        instance.delete()  # Uses soft delete functionality if defined in your model


class MessagesCountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        message_count = Message.objects.filter(Q(receiver=user) | Q(sender=user)).count()
        return response.Response({"message_count": message_count})
