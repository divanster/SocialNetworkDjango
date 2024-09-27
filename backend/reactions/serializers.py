# backend/reactions/serializers.py

from rest_framework import serializers
from .models import Reaction
from django.contrib.contenttypes.models import ContentType


class ReactionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    content_type = serializers.SlugRelatedField(
        slug_field='model',
        queryset=ContentType.objects.all()
    )
    object_id = serializers.UUIDField()

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'content_type', 'object_id', 'emoji', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_content_type(self, value):
        # Ensure that the content_type is valid for reactions
        # Add any custom validation if necessary
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        reaction, created = Reaction.objects.get_or_create(
            user=user,
            content_type=validated_data['content_type'],
            object_id=validated_data['object_id'],
            emoji=validated_data['emoji']
        )
        return reaction
