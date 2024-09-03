from rest_framework import viewsets, permissions
from .models import Message
from .serializers import MessageSerializer, MessageCountSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class MessagesCountView(APIView):
    serializer_class = MessageCountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Correctly filter using 'is_read' and 'receiver'
        count = Message.objects.filter(receiver=request.user, is_read=False).count()
        return Response({'count': count})
