# messenger/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter


@extend_schema(parameters=[OpenApiParameter(name='id', description='ID of the message', required=True, type=int,
                                            location=OpenApiParameter.PATH)])
class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(recipient=user) | Message.objects.filter(sender=user)
