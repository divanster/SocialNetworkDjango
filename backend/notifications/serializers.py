from rest_framework import serializers
from .models import Notification
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    Converts Django ORM model fields into a format suitable for JSON APIs.
    """
    notification_type = serializers.ChoiceField(
        choices=[choice[0] for choice in Notification.NOTIFICATION_TYPES]
    )
    sender_username = serializers.StringRelatedField(source='sender', read_only=True)
    receiver_username = serializers.StringRelatedField(source='receiver', read_only=True)
    content_object_url = serializers.SerializerMethodField()

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
            'content_object_url',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'sender_username',
            'receiver_username',
            'content_object_url',
        ]

    @extend_schema_field(serializers.URLField)
    def get_content_object_url(self, obj):
        """
        Retrieve the content object's URL if it exists.
        """
        return obj.get_content_object_url()

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
    Used to serialize the count of unread notifications for the user.
    """
    count = serializers.IntegerField(
        min_value=0,
        help_text="The number of unread notifications."
    )

    def validate_count(self, value):
        """
        Ensure the count value is non-negative.
        """
        if value < 0:
            raise serializers.ValidationError("Count cannot be negative.")
        return value
