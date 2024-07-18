# comments/views.py
from rest_framework import viewsets
from .models import Comment
from .serializers import CommentSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from notifications.utils import create_notification


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        create_notification(
            recipient=comment.recipe.author,
            actor=self.request.user,
            verb='commented on your recipe',
            target=comment.recipe.title
        )
