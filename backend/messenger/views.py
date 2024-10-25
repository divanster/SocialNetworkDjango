from django.db.models import Q  # Necessary for complex ORM queries with OR conditions
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
        return Message.objects.filter(Q(receiver_id=user.id) | Q(sender_id=user.id))

    def perform_create(self, serializer):
        instance = serializer.save(sender_id=self.request.user.id,
                                   sender_username=self.request.user.username)
        logger.info(f"Message created: {instance}")

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(f"Message updated: {instance}")

    def perform_destroy(self, instance):
        logger.info(f"Deleting message: {instance}")
        instance.delete()


# Adding the missing MessagesCountView
class MessagesCountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        message_count = Message.objects.filter(
            Q(receiver_id=user.id) | Q(sender_id=user.id)).count()
        return response.Response({"message_count": message_count})
