from rest_framework import serializers
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    # Use related field to directly reference usernames
    sender_name = serializers.StringRelatedField(source='sender', read_only=True)
    receiver_name = serializers.StringRelatedField(source='receiver', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'sender_name', 'receiver_name',
                  'content', 'created_at', 'is_read']
        read_only_fields = ['id', 'sender', 'sender_name', 'receiver_name', 'created_at']


class MessageCountSerializer(serializers.Serializer):
    """
    Serializer for counting the number of messages.
    """
    count = serializers.IntegerField()
