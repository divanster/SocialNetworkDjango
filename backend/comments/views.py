from rest_framework import viewsets, permissions
from .models import Comment
from .serializers import CommentSerializer
from .tasks import process_new_comment  # Import the Celery task


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        # Trigger the Celery task after the comment is created
        process_new_comment.delay(comment.id)  # Execute the task asynchronously
