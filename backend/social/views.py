from core.choices import VisibilityChoices
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Post
from .serializers import PostSerializer
from .tasks import process_kafka_message, \
    send_post_event_to_kafka  # Import the Celery task
from core.permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, and managing posts.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """
        Custom queryset to return posts based on visibility settings.
        """
        user = self.request.user

        if user.is_authenticated:
            # Get posts that are either public, posted by friends, or user's own posts
            return Post.objects.visible_to_user(user).order_by('-created_at')
        else:
            # If the user is not authenticated, they can only see public posts
            return Post.objects.filter(visibility=VisibilityChoices.PUBLIC).order_by('-created_at')

    @extend_schema(
        responses=PostSerializer
    )
    def perform_create(self, serializer):
        """
        Save the post with the user set to the current user,
        then trigger the Celery task to handle any background processing.
        """
        post = serializer.save(user=self.request.user)
        # Trigger the Celery task to send an event to Kafka
        send_post_event_to_kafka.delay(post.id, 'created')

    @extend_schema(
        parameters=[
            OpenApiParameter("pk", type=int, description="ID of the post")
        ],
        responses=PostSerializer
    )
    def perform_update(self, serializer):
        """
        Update the post and handle authorization to make sure
        that only the user can edit their post.
        """
        post = self.get_object()
        if post.user != self.request.user:  # Changed `author` to `user`
            raise permissions.PermissionDenied(
                "You do not have permission to edit this post.")

        serializer.save()

    @extend_schema(
        parameters=[
            OpenApiParameter("pk", type=int, description="ID of the post")
        ],
        responses={"204": "Post deleted successfully."}
    )
    def perform_destroy(self, instance):
        """
        Delete the post and ensure that only the user can delete their post.
        """
        if instance.user != self.request.user:  # Changed `author` to `user`
            raise permissions.PermissionDenied(
                "You do not have permission to delete this post.")

        instance.delete()
