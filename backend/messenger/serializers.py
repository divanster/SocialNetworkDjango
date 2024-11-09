from rest_framework import serializers
from .models import Message, Conversation
from django.contrib.auth import get_user_model

User = get_user_model()


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at']
        read_only_fields = ['id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    # Use related field to directly reference usernames
    sender_name = serializers.StringRelatedField(source='sender', read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'content',
                  'created_at', 'is_read']
        read_only_fields = ['id', 'sender', 'sender_name', 'created_at']


class MessagesCountSerializer(serializers.Serializer):
    """
    Serializer for counting the number of messages.
    """
    count = serializers.IntegerField()
