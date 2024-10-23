from rest_framework import viewsets, permissions
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
        return Message.objects.filter((Message.receiver_id == user.id) | (Message.sender_id == user.id))

    def perform_create(self, serializer):
        instance = serializer.save(sender_id=self.request.user.id, sender_username=self.request.user.username)
        logger.info(f"Message created: {instance}")

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(f"Message updated: {instance}")

    def perform_destroy(self, instance):
        logger.info(f"Deleting message: {instance}")
        instance.delete()
