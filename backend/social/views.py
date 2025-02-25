# backend/social/views.py

import logging
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from social.models import Post, PostImage, Rating
from social.serializers import PostSerializer, PostImageSerializer, RatingSerializer
from core.permissions import IsAuthorOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from core.choices import VisibilityChoices  # Import VisibilityChoices
from django.db import models  # Import models for models.Q if used
from rest_framework.exceptions import ValidationError
# Initialize logger
logger = logging.getLogger(__name__)


class PostViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and managing posts.
    Includes soft deletion and restoration functionalities.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    # Add JSONParser along with MultiPartParser and FormParser so JSON requests are accepted.
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):
        """
        Custom queryset to return posts based on visibility settings.
        """
        user = self.request.user
        if user.is_authenticated:
            # Get posts visible to the user.
            return Post.objects.visible_to_user(user).order_by('-created_at')
        else:
            return Post.objects.filter(visibility=VisibilityChoices.PUBLIC).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Save the post with the user set to the current user.
        """
        serializer.save(user=self.request.user)
        logger.info(f"Post created by user {self.request.user.id}")

    def perform_update(self, serializer):
        """
        Update the post ensuring that only the post owner can edit.
        """
        post = self.get_object()
        if post.user != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this post.")
        serializer.save()
        logger.info(f"Post with ID {post.id} updated by user {self.request.user.id}")

    def perform_destroy(self, instance):
        """
        Soft delete the post ensuring only the post owner can delete it.
        Admin users can delete any post.
        """
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied(
                "You do not have permission to delete this post.")
        instance.delete()  # Soft delete
        logger.info(
            f"Post with ID {instance.id} soft-deleted by user {self.request.user.id}")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type="string",  # UUID as string
                location=OpenApiParameter.PATH,
                description="UUID of the message"
            ),
        ],
        responses=PostSerializer,
    )
    def retrieve(self, request, id=None):
        """
        Retrieve a specific post by its UUID.
        """
        post = self.get_object()
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restore', permission_classes=[permissions.IsAdminUser])
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted post. Only accessible to admin users.
        """
        try:
            post = Post.all_objects.get(pk=pk, is_deleted=True)
            post.restore()
            serializer = self.get_serializer(post)
            logger.info(f"Post with ID {post.id} restored by admin user {request.user.id}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {pk} does not exist or is not deleted.")
            return Response({"detail": "Post not found or not deleted."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='all-deleted', permission_classes=[permissions.IsAdminUser])
    def list_deleted(self, request):
        """
        List all soft-deleted posts. Only accessible to admin users.
        """
        deleted_posts = Post.all_objects.filter(is_deleted=True).order_by('-deleted_at')
        serializer = self.get_serializer(deleted_posts, many=True)
        logger.info(f"Admin user {request.user.id} retrieved all soft-deleted posts.")
        return Response(serializer.data, status=status.HTTP_200_OK)



class PostImageViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and managing post images.
    Includes soft deletion and restoration functionalities.
    """
    serializer_class = PostImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """
        Returns post images based on soft deletion status and user permissions.
        """
        user = self.request.user

        if user.is_authenticated:
            # Users can see their own images and images of public posts
            return PostImage.objects.filter(
                models.Q(post__user=user) | models.Q(post__visibility=VisibilityChoices.PUBLIC)
            ).order_by('-created_at')
        else:
            # Anonymous users can only see images of public posts
            return PostImage.objects.filter(post__visibility=VisibilityChoices.PUBLIC).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Save the post image and associate it with the current user.
        """
        post = serializer.validated_data.get('post')
        if post.user != self.request.user:
            raise permissions.PermissionDenied("You can only add images to your own posts.")
        serializer.save()
        logger.info(f"PostImage added to post {post.id} by user {self.request.user.id}")

    def perform_update(self, serializer):
        """
        Update the post image and ensure only the post owner can edit it.
        """
        post_image = self.get_object()
        if post_image.post.user != self.request.user:
            raise permissions.PermissionDenied("You can only edit images of your own posts.")
        serializer.save()
        logger.info(f"PostImage with ID {post_image.id} updated by user {self.request.user.id}")

    def perform_destroy(self, instance):
        """
        Soft delete the post image and ensure only the post owner can delete it.
        """
        if instance.post.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete images of your own posts.")
        instance.delete()  # Soft delete
        logger.info(f"PostImage with ID {instance.id} soft-deleted by user {self.request.user.id}")

    @action(detail=True, methods=['post'], url_path='restore', permission_classes=[permissions.IsAdminUser])
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted post image. Only accessible to admin users.
        """
        try:
            post_image = PostImage.all_objects.get(pk=pk, is_deleted=True)
            post_image.restore()
            serializer = self.get_serializer(post_image)
            logger.info(f"PostImage with ID {post_image.id} restored by admin user {request.user.id}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PostImage.DoesNotExist:
            logger.error(f"PostImage with ID {pk} does not exist or is not deleted.")
            return Response({"detail": "PostImage not found or not deleted."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='all-deleted', permission_classes=[permissions.IsAdminUser])
    def list_deleted(self, request):
        """
        List all soft-deleted post images. Only accessible to admin users.
        """
        deleted_images = PostImage.all_objects.filter(is_deleted=True).order_by('-deleted_at')
        serializer = self.get_serializer(deleted_images, many=True)
        logger.info(f"Admin user {request.user.id} retrieved all soft-deleted post images.")
        return Response(serializer.data, status=status.HTTP_200_OK)


class RatingViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and managing ratings.
    Includes soft deletion and restoration functionalities.
    """
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        """
        Returns ratings based on soft deletion status and user permissions.
        """
        user = self.request.user

        if user.is_authenticated:
            # Users can see ratings for their posts and ratings of public posts
            return Rating.objects.filter(
                models.Q(post__user=user) | models.Q(post__visibility=VisibilityChoices.PUBLIC)
            ).order_by('-created_at')
        else:
            # Anonymous users can only see ratings of public posts
            return Rating.objects.filter(post__visibility=VisibilityChoices.PUBLIC).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Create a rating ensuring a user can rate a post only once.
        """
        post = serializer.validated_data.get('post')
        user = self.request.user

        if post.user == user:
            raise ValidationError("You cannot rate your own post.")

        if Rating.objects.filter(post=post, user=user, is_deleted=False).exists():
            raise ValidationError("You have already rated this post.")

        serializer.save(user=user)
        logger.info(f"User {user.id} rated post {post.id} with value {serializer.validated_data.get('value')}")

    def perform_update(self, serializer):
        """
        Update a rating ensuring only the rating owner can update it.
        """
        rating = self.get_object()
        if rating.user != self.request.user:
            raise permissions.PermissionDenied("You can only update your own ratings.")
        serializer.save()
        logger.info(f"Rating with ID {rating.id} updated by user {self.request.user.id}")

    def perform_destroy(self, instance):
        """
        Soft delete the rating ensuring only the rating owner can delete it.
        """
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own ratings.")
        instance.delete()  # Soft delete
        logger.info(f"Rating with ID {instance.id} soft-deleted by user {self.request.user.id}")

    @action(detail=True, methods=['post'], url_path='restore', permission_classes=[permissions.IsAdminUser])
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted rating. Only accessible to admin users.
        """
        try:
            rating = Rating.all_objects.get(pk=pk, is_deleted=True)
            rating.restore()
            serializer = self.get_serializer(rating)
            logger.info(f"Rating with ID {rating.id} restored by admin user {request.user.id}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Rating.DoesNotExist:
            logger.error(f"Rating with ID {pk} does not exist or is not deleted.")
            return Response({"detail": "Rating not found or not deleted."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='all-deleted', permission_classes=[permissions.IsAdminUser])
    def list_deleted(self, request):
        """
        List all soft-deleted ratings. Only accessible to admin users.
        """
        deleted_ratings = Rating.all_objects.filter(is_deleted=True).order_by('-deleted_at')
        serializer = self.get_serializer(deleted_ratings, many=True)
        logger.info(f"Admin user {request.user.id} retrieved all soft-deleted ratings.")
        return Response(serializer.data, status=status.HTTP_200_OK)
