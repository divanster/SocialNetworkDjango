# backend/social/views.py
from core.choices import VisibilityChoices
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post
from .serializers import PostSerializer
from .tasks import process_new_post  # Import the Celery task
from core.permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, and managing posts.
    The posts are filtered based on their visibility:
    - Public posts can be seen by everyone.
    - Friend-only posts can be seen by the author's friends.
    - Private posts can only be seen by the author.
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
            return Post.objects.filter(visibility=VisibilityChoices.PUBLIC).order_by(
                '-created_at')

    def perform_create(self, serializer):
        """
        Save the post with the author set to the current user,
        then trigger the Celery task to handle any background processing.
        """
        post = serializer.save(author=self.request.user)
        # Trigger the Celery task after the post is created
        process_new_post.delay(post.id)  # Execute the task asynchronously

    def perform_update(self, serializer):
        """
        Update the post and handle authorization to make sure
        that only the author can edit their post.
        """
        post = self.get_object()
        if post.author != self.request.user:
            raise permissions.PermissionDenied(
                "You do not have permission to edit this post.")

        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete the post and ensure that only the author can delete their post.
        """
        if instance.author != self.request.user:
            raise permissions.PermissionDenied(
                "You do not have permission to delete this post.")

        instance.delete()
