# backend/follows/serializers.py

from rest_framework import serializers
from .models import Follow


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.PrimaryKeyRelatedField(read_only=True)
    followed = serializers.PrimaryKeyRelatedField(queryset=Follow.objects.none())

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']
        read_only_fields = ['id', 'follower', 'created_at']

    def __init__(self, *args, **kwargs):
        super(FollowSerializer, self).__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['followed'].queryset = User.objects.all()

    def validate_followed(self, value):
        user = self.context['request'].user
        if user == value:
            raise serializers.ValidationError("You cannot follow yourself.")
        return value
