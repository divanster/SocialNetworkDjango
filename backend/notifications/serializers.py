from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    Converts Django ORM model fields into a format suitable for JSON APIs.
    """
    notification_type = serializers.ChoiceField(
        choices=[choice[0] for choice in Notification.NOTIFICATION_TYPES])

    class Meta:
        model = Notification
        fields = [
            'id',
            'sender_id',
            'sender_username',
            'receiver_id',
            'receiver_username',
            'notification_type',
            'text',
            'is_read',
            'content_type',
            'object_id',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """
        Creates a Notification instance.
        """
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Updates a Notification instance.
        """
        return super().update(instance, validated_data)


class NotificationCountSerializer(serializers.Serializer):
    """
    Serializer for notification count.
    """
    count = serializers.IntegerField()
