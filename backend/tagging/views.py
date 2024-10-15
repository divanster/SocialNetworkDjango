# backend/tagging/test_views.py
from rest_framework import viewsets, permissions
from .models import TaggedItem
from .serializers import TaggedItemSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response


class TaggedItemViewSet(viewsets.ModelViewSet):
    queryset = TaggedItem.objects.all()
    serializer_class = TaggedItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')
        tagged_user_id = request.data.get('tagged_user')
        tagged_by = request.user

        try:
            content_type_obj = ContentType.objects.get(id=content_type)
        except ContentType.DoesNotExist:
            raise ValidationError("Invalid content type.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Custom logic to ensure unique tagging
        if TaggedItem.objects.filter(
                content_type=content_type_obj,
                object_id=object_id,
                tagged_user_id=tagged_user_id
        ).exists():
            raise ValidationError("This user is already tagged on this object.")

        # Save the tag
        self.perform_create(serializer)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(tagged_by=self.request.user)
