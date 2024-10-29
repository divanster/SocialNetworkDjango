# backend/pages/views.py
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Page
from .serializers import PageSerializer
import logging

logger = logging.getLogger(__name__)


class PageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, editing, and deleting pages.
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Optionally restricts the returned pages to those created by the logged-in user.
        """
        queryset = Page.objects.all()
        user = self.request.user
        if user.is_authenticated:
            return queryset.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        """
        Override the default perform_create to associate the page with the user.
        """
        serializer.save(user=self.request.user)
        logger.info(f"Page created by user {self.request.user.username}")

    def perform_update(self, serializer):
        """
        Override the default perform_update to enforce ownership of pages.
        """
        instance = serializer.instance
        if instance.user != self.request.user:
            logger.warning(
                f"[VIEW] Unauthorized update attempt on Page ID {instance.id} by user {self.request.user.id}")
            raise PermissionDenied("You do not have permission to edit this page.")

        serializer.save()
        logger.info(f"Page updated by user {self.request.user.username}")

    def perform_destroy(self, instance):
        """
        Override the default perform_destroy to enforce ownership of pages.
        """
        if instance.user != self.request.user:
            logger.warning(
                f"[VIEW] Unauthorized delete attempt on Page ID {instance.id} by user {self.request.user.id}")
            raise PermissionDenied("You do not have permission to delete this page.")

        instance.delete()
        logger.info(f"Page deleted by user {self.request.user.username}")

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def my_pages(self, request):
        """
        Custom action to get pages belonging to the currently authenticated user.
        """
        user_pages = Page.objects.filter(user=request.user)
        serializer = self.get_serializer(user_pages, many=True)
        return Response(serializer.data)

