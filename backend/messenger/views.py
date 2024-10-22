from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Message
from .serializers import MessageSerializer, MessageCountSerializer


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Override the default queryset to return only messages that are related to the authenticated user.
        The user can see messages that they have sent or received.
        """
        user = self.request.user
        return Message.objects.filter(
            receiver_id=user.id
        ) | Message.objects.filter(sender_id=user.id)

    def perform_create(self, serializer):
        """
        Custom method to save a new message, automatically setting the sender to the current authenticated user.
        """
        serializer.save(sender_id=self.request.user.id, sender_username=self.request.user.username)

    def perform_destroy(self, instance):
        """
        Custom method to check if the requesting user is authorized to delete the message.
        A user can only delete a message that they have sent.
        """
        if instance.sender_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to delete this message.")
        instance.delete()


class MessagesCountView(APIView):
    """
    API View to get the count of unread messages for the authenticated user.
    """
    serializer_class = MessageCountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Retrieve the count of unread messages for the authenticated user.
        """
        count = Message.objects.filter(receiver_id=request.user.id, is_read=False).count()
        return Response({'count': count})
