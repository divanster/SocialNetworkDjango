# backend/messenger/serializers.py
from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'sender', 'timestamp']


class MessageCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()

