from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""

    class Meta:
        model = Comment
        fields = ['id', 'user', 'recipe', 'text', 'created_at']
        read_only_fields = ['id', 'user', 'recipe', 'created_at']
