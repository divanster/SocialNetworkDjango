# backend/pages/serializers.py
from rest_framework import serializers
from .models import Page


class PageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Page model.
    It handles conversion from Python objects (Django model instances)
    to JSON format suitable for use in APIs, and vice versa.
    """
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Page
        fields = [
            'id',
            'user',
            'user_username',
            'title',
            'content',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_username', 'created_at', 'updated_at']
