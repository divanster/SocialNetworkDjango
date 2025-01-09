from rest_framework import serializers
from .models import Notification
from django.contrib.auth import get_user_model
from friends.models import Block  # Import Block model to validate sender-receiver relationships
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
        if obj.content_object:
            return obj.content_object.get_absolute_url()  # Assumes related objects have get_absolute_url
        return None

    def validate_receiver(self, value):
        """
        Ensure that the receiver is not blocked by the sender.
        """
        sender = self.context['request'].user
        if Block.objects.filter(blocker=sender, blocked=value).exists():
            raise serializers.ValidationError("You have blocked this user and cannot send notifications to them.")
        return value

    def create(self, validated_data):
        """
        Creates a Notification instance with the sender set to the authenticated user.
        """
        sender = self.context['request'].user
        receiver = validated_data.get('receiver')
        notification_type = validated_data.get('notification_type')
        text = validated_data.get('text', '')

        notification = Notification.objects.create(
            sender=sender,
            receiver=receiver,
            notification_type=notification_type,
            text=text,
            content_type=validated_data.get('content_type'),
            object_id=validated_data.get('object_id')
        )
        return notification

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
