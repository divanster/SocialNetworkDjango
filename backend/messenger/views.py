# backend/messenger/views.py
from rest_framework import viewsets, permissions
from .models import Message
from .serializers import MessageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MessageCountSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class MessagesCountView(APIView):
    serializer_class = MessageCountSerializer

    def get(self, request):
        count = Message.objects.filter(user=request.user, read=False).count()
        return Response({'count': count})
