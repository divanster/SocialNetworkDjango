# backend/core/viewsets.py

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsAuthorOrReadOnly
from .pagination import StandardResultsSetPagination


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    A base viewset that provides default `create()`, `retrieve()`,
    `update()`, `partial_update()`, `destroy()` and `list()` actions.
    """
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^name', '^title']
    ordering_fields = ['id', 'created_at']
    ordering = ['-created_at']

    # Override methods if common customizations are needed
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    # Add any additional common methods or overrides here

