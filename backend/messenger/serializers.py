# backend/messages/serializers.py

from rest_framework import serializers
from .models import Message
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from friends.models import \
    Block  # Import Block model to validate sender-receiver relationships

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)
    sender_full_name = serializers.SerializerMethodField()
    receiver_full_name = serializers.SerializerMethodField()
    sender_profile_picture = serializers.SerializerMethodField()
    receiver_profile_picture = serializers.SerializerMethodField()
    read = serializers.BooleanField(source='is_read',
                                    read_only=True)  # Alias for frontend consistency

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'sender_name', 'receiver_name',
            'sender_full_name', 'receiver_full_name',
            'sender_profile_picture', 'receiver_profile_picture',
            'content', 'read',
            # Changed from 'is_read' to 'read' for frontend compatibility
            'created_at'
        ]
        read_only_fields = [
            'id', 'sender', 'sender_name', 'receiver_name', 'created_at', 'read'
        ]

    def _full_name_for_user(self, user):
        try:
            profile = user.profile
        except (AttributeError, ObjectDoesNotExist):
            profile = None
        if profile:
            full_name = f"{profile.first_name} {profile.last_name}".strip()
            if full_name:
                return full_name
        return user.username

    def _profile_picture_for_user(self, user):
        try:
            profile = user.profile
        except (AttributeError, ObjectDoesNotExist):
            profile = None
        if not profile or not profile.profile_picture:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(profile.profile_picture.url)
        return profile.profile_picture.url

    def get_sender_full_name(self, obj):
        return self._full_name_for_user(obj.sender)

    def get_receiver_full_name(self, obj):
        return self._full_name_for_user(obj.receiver)

    def get_sender_profile_picture(self, obj):
        return self._profile_picture_for_user(obj.sender)

    def get_receiver_profile_picture(self, obj):
        return self._profile_picture_for_user(obj.receiver)

    def validate_receiver(self, value):
        """
        Ensure that the receiver is not blocked by the sender.
        """
        user = self.context['request'].user
        if value == user:
            return value
        if Block.objects.filter(blocker=user, blocked=value).exists():
            raise serializers.ValidationError(
                "You have blocked this user and cannot send messages to them."
            )
        if Block.objects.filter(blocker=value, blocked=user).exists():
            raise serializers.ValidationError(
                "This user has blocked you."
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
