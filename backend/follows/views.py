# backend/follows/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Follow
from .serializers import FollowSerializer
import logging

logger = logging.getLogger(__name__)

class FollowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Follow relationships between users.
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned follows based on query parameters.
        Only non-deleted follows are returned due to SoftDeleteManager.
        """
        queryset = Follow.objects.all()
        follower_id = self.request.query_params.get('follower_id')
        followed_id = self.request.query_params.get('followed_id')

        if follower_id:
            queryset = queryset.filter(follower_id=follower_id)
        if followed_id:
            queryset = queryset.filter(followed_id=followed_id)

        return queryset

    def perform_create(self, serializer):
        """
        Create a new Follow relationship.
        The task is now triggered via signals, not here.
        """
        instance = serializer.save(follower=self.request.user)

        # Notify the followed user about the new follower
        logger.info(f"[VIEW] Created Follow with ID {instance.id}")
        # The task is triggered by the signal, no need to handle it directly in the view.

    def perform_destroy(self, instance):
        """
        Perform a soft delete on a Follow relationship.
        The task is now triggered via signals, not here.
        """
        if instance.follower != self.request.user:
            logger.warning(
                f"[VIEW] Unauthorized delete attempt on Follow ID {instance.id} by user {self.request.user.id}"
            )
            raise PermissionDenied("You do not have permission to unfollow this user.")

        # Log the soft delete
        logger.info(f"[VIEW] Soft deleting Follow with ID {instance.id}")
        instance.delete()  # This performs a soft delete
        # The task is triggered by the signal, no need to handle it directly in the view.

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method to handle not found follow relationships explicitly.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            logger.error(
                f"[VIEW] Attempted to delete non-existent Follow ID {kwargs.get('pk')}"
            )
            raise NotFound("Follow relationship not found.")
