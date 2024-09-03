# backend/messenger/serializers.py
from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    # Add fields to include sender's and receiver's usernames
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = Message
        # Include sender_name and receiver_name in the fields
        fields = ['id', 'sender', 'receiver', 'sender_name', 'receiver_name', 'content',
                  'timestamp', 'is_read']
        read_only_fields = ['id', 'sender', 'sender_name', 'receiver_name', 'timestamp']


class MessageCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()
