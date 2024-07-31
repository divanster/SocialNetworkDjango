# backend/notifications/serializers.py
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'receiver', 'notification_type', 'text', 'created_at', 'is_read']
        read_only_fields = ['id', 'sender', 'created_at']


class NotificationCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()
