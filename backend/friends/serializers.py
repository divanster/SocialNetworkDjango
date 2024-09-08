# backend/friends/serializers.py
from rest_framework import serializers
from .models import FriendRequest, Friendship


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'created_at', 'status']
        read_only_fields = ['id', 'created_at', 'status']


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['id', 'user1', 'user2', 'created_at']
        read_only_fields = ['id', 'user1', 'user2', 'created_at']
