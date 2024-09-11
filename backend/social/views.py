from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post
from .serializers import PostSerializer
from .tasks import process_new_post  # Import the Celery task


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        # Trigger the Celery task after the post is created
        process_new_post.delay(post.id)  # Execute the task asynchronously
