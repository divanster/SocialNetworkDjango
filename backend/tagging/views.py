from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import TaggedItem
from .serializers import TaggedItemSerializer


class TaggedItemViewSet(viewsets.ModelViewSet):
    serializer_class = TaggedItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return TaggedItem.objects.filter(
            Q(tagged_by=user) | Q(tagged_user=user)
        ).select_related('tagged_user', 'tagged_by', 'content_type')

    def perform_create(self, serializer):
        serializer.save(tagged_by=self.request.user)

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.tagged_by != user and instance.tagged_user != user:
            raise PermissionDenied("You do not have permission to remove this tag.")
        instance.delete()
