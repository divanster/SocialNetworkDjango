from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender_username', read_only=True)
    receiver_name = serializers.CharField(source='receiver_username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'receiver_id', 'sender_name', 'receiver_name',
                  'content',
                  'timestamp', 'is_read']
        read_only_fields = ['id', 'sender_id', 'sender_name', 'receiver_name',
                            'timestamp']


class MessageCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()
