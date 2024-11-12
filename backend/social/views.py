from django.db import models  # Importing Django models
from core.models.base_models import SoftDeleteManager  # Import SoftDeleteManager
from core.choices import VisibilityChoices
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Post
from .serializers import PostSerializer
from core.permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, and managing posts.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        """
        Custom queryset to return posts based on visibility settings.
        """
        user = self.request.user

        if user.is_authenticated:
            return Post.objects.filter(is_deleted=False).visible_to_user(user).order_by('-created_at')
        else:
            return Post.objects.filter(is_deleted=False, visibility=VisibilityChoices.PUBLIC).order_by('-created_at')

    def check_author_permission(self, post):
        """
        Helper method to ensure that the current user is the author of the post.
        Raises a PermissionDenied error if the user is not the author.
        """
        if post.author != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to modify this post.")

    @extend_schema(responses=PostSerializer)
    def perform_create(self, serializer):
        """
        Save the post with the author set to the current user.
        """
        serializer.save(author=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter("pk", type=int, description="ID of the post")
        ],
        responses=PostSerializer
    )
    def perform_update(self, serializer):
        """
        Update the post and ensure that only the author can edit their post.
        """
        post = self.get_object()
        self.check_author_permission(post)  # Check if the user has permission to edit
        serializer.save()

    @extend_schema(
        parameters=[
            OpenApiParameter("pk", type=int, description="ID of the post")
        ],
        responses={"204": "Post deleted successfully."}
    )
    def perform_destroy(self, instance):
        """
        Delete the post and ensure that only the author can delete their post.
        """
        self.check_author_permission(instance)
        instance.delete()  # Soft delete
        print(f"Post with ID: {instance.id} deleted.")


# Soft Delete Model Adjustments

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])  # Avoid unnecessary commits

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)
