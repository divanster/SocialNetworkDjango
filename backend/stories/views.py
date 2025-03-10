from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Story
from .serializers import StorySerializer
from core.permissions import IsAuthorOrReadOnly  # Use globally available permission
import logging

logger = logging.getLogger(__name__)


class StoryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, and managing stories.
    Stories can be visible to everyone (public), to friends of the author (friends-only),
    or only to the author (private).
    """
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Custom queryset to return stories based on visibility settings.
        Public stories are visible to everyone.
        Friend-only stories are visible to friends.
        Private stories are visible only to the author.
        """
        user = self.request.user
        return Story.objects.visible_to_user(user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Save the story with the author set to the current user.
        """
        serializer.save(user=self.request.user)
        logger.info(
            f"Story created by user {self.request.user.username} with ID {serializer.instance.id}")

    def perform_update(self, serializer):
        """
        Update the story instance.
        """
        serializer.save()
        logger.info(
            f"Story updated by user {self.request.user.username} with ID {serializer.instance.id}")

    def perform_destroy(self, instance):
        """
        Delete the story instance.
        """
        instance.delete()
        logger.info(
            f"Story deleted by user {self.request.user.username} with ID {instance.id}")
