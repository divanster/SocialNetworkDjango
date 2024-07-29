# backend/reactions/serializers.py
from rest_framework import serializers
from .models import Reaction


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'post', 'emoji', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
