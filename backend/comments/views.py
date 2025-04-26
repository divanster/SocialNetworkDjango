from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from django.contrib.contenttypes.models import ContentType

from social.models import Post
from .models import Comment
from .serializers import CommentSerializer
import logging

logger = logging.getLogger(__name__)

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Comment CRUD operations.
    Filters by post_id via content_type + object_id.
    Requires `post_id` on create.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx.update({"request": self.request})
        return ctx

    def get_queryset(self):
        """
        Custom queryset for fetching comments based on `object_id`.
        """
        qs = super().get_queryset()
        post_id = self.request.query_params.get("post_id")
        if post_id:
            qs = qs.filter(object_id=post_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            logger.warning("[VIEW] Unauthorized comment creation attempt")
            raise PermissionDenied("You need to be logged in to create a comment.")

        # Allow for object_id to be passed either as a part of body or query params
        post_id = (
            self.request.data.get("post_id")
            or self.request.query_params.get("post_id")
            or self.request.data.get("object_id")  # Accept object_id for compatibility
        )
        if not post_id:
            raise ValidationError("`post_id` or `object_id` is required to create a comment.")

        post_ct = ContentType.objects.get_for_model(Post)  # Get content type for Post
        instance = serializer.save(
            user=user,
            content_type=post_ct,
            object_id=post_id
        )
        logger.info(f"[VIEW] Created Comment with ID {instance.id}")

    def perform_update(self, serializer):
        inst = serializer.instance
        if inst.user != self.request.user:
            logger.warning(f"[VIEW] Unauthorized update attempt on Comment ID {inst.id}")
            raise PermissionDenied("You do not have permission to edit this comment.")
        updated = serializer.save()
        logger.info(f"[VIEW] Updated Comment with ID {updated.id}")

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            logger.warning(f"[VIEW] Unauthorized delete attempt on Comment ID {instance.id}")
            raise PermissionDenied("You do not have permission to delete this comment.")
        instance.delete()
        logger.info(f"[VIEW] Deleted Comment with ID {instance.id}")

    def destroy(self, request, *args, **kwargs):
        try:
            inst = self.get_object()
            self.perform_destroy(inst)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            logger.error(f"[VIEW] Tried to delete non-existent Comment ID {kwargs.get('pk')}")
            raise NotFound("Comment not found.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        inst = self.get_object()
        if inst.user != request.user:
            logger.warning(f"[VIEW] Unauthorized update attempt on Comment ID {inst.id}")
            raise PermissionDenied("You do not have permission to update this comment.")
        serializer = self.get_serializer(inst, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
