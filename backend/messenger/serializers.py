# backend/messages/serializers.py

from rest_framework import serializers
from .models import Message
from django.contrib.auth import get_user_model
from friends.models import \
    Block  # Import Block model to validate sender-receiver relationships

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.StringRelatedField(source='sender', read_only=True)
    receiver_name = serializers.StringRelatedField(source='receiver', read_only=True)
    read = serializers.BooleanField(source='is_read',
                                    read_only=True)  # Alias for frontend consistency

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'sender_name', 'receiver_name',
            'content', 'read',
            # Changed from 'is_read' to 'read' for frontend compatibility
            'created_at'
        ]
        read_only_fields = [
            'id', 'sender', 'sender_name', 'receiver_name', 'created_at', 'read'
        ]

    def validate_receiver(self, value):
        """
        Ensure that the receiver is not blocked by the sender.
        """
        user = self.context['request'].user
        if Block.objects.filter(blocker=user, blocked=value).exists():
            raise serializers.ValidationError(
                "You have blocked this user and cannot send messages to them."
            )
        return value

    def create(self, validated_data):
        """
        Override the create method to set the sender to the authenticated user.
        """
        sender = self.context['request'].user
        receiver = validated_data.get('receiver')
        content = validated_data.get('content')
        message = Message.objects.create(sender=sender, receiver=receiver,
                                         content=content)
        return message


class MessagesCountSerializer(serializers.Serializer):
    """
    Serializer for counting the number of messages.
    """
    count = serializers.IntegerField()
