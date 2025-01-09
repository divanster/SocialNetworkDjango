from rest_framework import serializers

from friends.models import Block
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.StringRelatedField(source='sender', read_only=True)
    receiver_name = serializers.StringRelatedField(source='receiver', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'sender_name', 'receiver_name',
            'content', 'created_at', 'is_read'
        ]
        read_only_fields = [
            'id', 'sender', 'sender_name', 'receiver_name', 'created_at'
        ]

    def validate_receiver(self, value):
        """
        Ensure that the receiver is not blocked by the sender.
        """
        user = self.context['request'].user
        if Block.objects.filter(blocker=user, blocked=value).exists():
            raise serializers.ValidationError(
                "You have blocked this user and cannot send messages to them.")
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
