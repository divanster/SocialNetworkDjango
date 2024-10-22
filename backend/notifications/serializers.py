# backend/notifications/serializers.py

from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.Serializer):
    """
    Serializer for the Notification model.
    Converts MongoEngine Document fields into a format suitable for JSON APIs.
    """
    id = serializers.CharField(read_only=True)
    sender_id = serializers.IntegerField()
    sender_username = serializers.CharField(max_length=150)
    receiver_id = serializers.IntegerField()
    receiver_username = serializers.CharField(max_length=150)
    notification_type = serializers.ChoiceField(choices=[choice[0] for choice in Notification.NOTIFICATION_TYPES])
    text = serializers.CharField(required=False, allow_blank=True)
    is_read = serializers.BooleanField(default=False)
    content_type = serializers.CharField(max_length=100, required=False, allow_blank=True)
    object_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Notification(**validated_data).save()

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class NotificationCountSerializer(serializers.Serializer):
    """
    Serializer for notification count.
    """
    count = serializers.IntegerField()
