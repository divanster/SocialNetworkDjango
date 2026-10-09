# backend/follows/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.PrimaryKeyRelatedField(read_only=True)
    followed = serializers.PrimaryKeyRelatedField(queryset=Follow.objects.none(), required=False)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Follow.objects.none(),
        source='followed',
        required=False
    )

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'user_id', 'created_at']
        read_only_fields = ['id', 'follower', 'created_at']

    def __init__(self, *args, **kwargs):
        super(FollowSerializer, self).__init__(*args, **kwargs)
        User = get_user_model()
        self.fields['followed'].queryset = User.objects.all()
        self.fields['user_id'].queryset = User.objects.all()

    def validate(self, attrs):
        followed = attrs.get('followed')
        if not followed:
            raise serializers.ValidationError({'followed': 'This field is required.'})

        user = self.context['request'].user
        if user == followed:
            raise serializers.ValidationError("You cannot follow yourself.")

        existing = Follow.all_objects.filter(follower=user, followed=followed).first()
        if existing and not existing.is_deleted:
            raise serializers.ValidationError("You are already following this user.")
        return attrs

    def create(self, validated_data):
        follower = self.context['request'].user
        followed = validated_data['followed']
        existing = Follow.all_objects.filter(follower=follower, followed=followed).first()
        if existing:
            if existing.is_deleted:
                existing.restore()
                return existing
            raise serializers.ValidationError("You are already following this user.")
        return Follow.objects.create(follower=follower, followed=followed)
