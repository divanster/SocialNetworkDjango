# backend/stories/views.py
from datetime import datetime

from rest_framework import viewsets, permissions
from .models import Story
from .serializers import StorySerializer


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.using('social_db').all()
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(
            user_id=self.request.user.id,
            user_username=self.request.user.username,
            created_at=datetime.now()
        )
