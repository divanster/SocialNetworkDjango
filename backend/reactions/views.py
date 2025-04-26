from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.contenttypes.models import ContentType
from .models import Reaction
from .serializers import ReactionSerializer
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

class ReactionViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    A viewset for viewing and editing Reaction instances.
    """
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Reaction.objects.all()
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')

        if content_type and object_id:
            try:
                content_type_obj = ContentType.objects.get(model=content_type)
                queryset = queryset.filter(content_type=content_type_obj,
                                           object_id=object_id)
            except ContentType.DoesNotExist:
                queryset = Reaction.objects.none()

        return queryset

    def perform_create(self, serializer):
        content_type = self.request.data.get('content_type')
        object_id = self.request.data.get('object_id')
        emoji = self.request.data.get('emoji')

        try:
            content_type_obj = ContentType.objects.get(model=content_type)
        except ContentType.DoesNotExist:
            return Response({"error": "Invalid content type."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not emoji:
            return Response({"error": "Emoji is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the reaction already exists, toggle if it does
        existing_reaction = Reaction.objects.filter(
            user=self.request.user,
            content_type=content_type_obj,
            object_id=object_id,
            emoji=emoji
        )

        if existing_reaction.exists():
            existing_reaction.delete()  # Toggle behavior
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer.save(
            user=self.request.user,
            content_type=content_type_obj,
            object_id=object_id
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'],
            permission_classes=[permissions.IsAuthenticated])
    def remove_reaction(self, request):
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')
        emoji = request.data.get('emoji')

        if not content_type or not object_id or not emoji:
            return Response(
                {"error": "Content type, object ID, and emoji are required."},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type_obj = ContentType.objects.get(model=content_type)
        except ContentType.DoesNotExist:
            return Response({"error": "Invalid content type."},
                            status=status.HTTP_400_BAD_REQUEST)

        reaction = get_object_or_404(
            Reaction,
            user=request.user,
            content_type=content_type_obj,
            object_id=object_id,
            emoji=emoji
        )
        reaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
