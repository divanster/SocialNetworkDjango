from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Comment
from .serializers import CommentSerializer
import logging

logger = logging.getLogger(__name__)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Comment CRUD operations.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        """
        Add additional context for the serializer to have access to the request.
        This will be useful for tagging.
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        """
        Override the default queryset to allow filtering by the post ID
        provided in the request query parameters.
        """
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        """
        Overridden perform_create method to save a new comment.
        Kafka task is triggered via signals.
        """
        if not self.request.user.is_authenticated:
            logger.warning("[VIEW] Unauthorized comment creation attempt")
            raise PermissionDenied("You need to be logged in to create a comment.")

        instance = serializer.save(user=self.request.user)
        logger.info(f"[VIEW] Created Comment with ID {instance.id}")

    def perform_update(self, serializer):
        """
        Overridden perform_update method to ensure only the comment's owner can update.
        Kafka task is triggered via signals.
        """
        instance = serializer.instance
        if instance.user != self.request.user:
            logger.warning(
                f"[VIEW] Unauthorized update attempt on Comment ID {instance.id} by user {self.request.user.id}"
            )
            raise PermissionDenied("You do not have permission to edit this comment.")

        updated_instance = serializer.save()
        logger.info(f"[VIEW] Updated Comment with ID {updated_instance.id}")

    def perform_destroy(self, instance):
        """
        Overridden perform_destroy method to ensure only the comment's owner can delete.
        Kafka task is triggered via signals.
        """
        if instance.user != self.request.user:
            logger.warning(
                f"[VIEW] Unauthorized delete attempt on Comment ID {instance.id} by user {self.request.user.id}"
            )
            raise PermissionDenied("You do not have permission to delete this comment.")

        instance.delete()
        logger.info(f"[VIEW] Deleted Comment with ID {instance.id}")

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method to handle explicit responses when a comment is not found.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            logger.error(
                f"[VIEW] Attempted to delete non-existent Comment ID {kwargs.get('pk')}"
            )
            raise NotFound("Comment not found.")

    def update(self, request, *args, **kwargs):
        """
        Custom update method to ensure the correct response and permission handling.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Ensure the user trying to update the comment is the owner
        if instance.user != request.user:
            logger.warning(
                f"[VIEW] Unauthorized update attempt on Comment ID {instance.id} by user {request.user.id}"
            )
            raise PermissionDenied("You do not have permission to update this comment.")

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
