# backend/friends/serializers.py
from rest_framework import serializers
from .models import FriendRequest, Friendship


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender_id', 'receiver_id', 'created_at', 'status']
        read_only_fields = ['id', 'created_at', 'status']


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['id', 'user1_id', 'user2_id', 'created_at']
        read_only_fields = ['id', 'user1_id', 'user2_id', 'created_at']
