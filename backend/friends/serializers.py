from rest_framework import serializers
from .models import FriendRequest, Friendship, Block
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    receiver_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source='receiver'
    )

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'receiver_id', 'created_at', 'status']
        read_only_fields = ['id', 'sender', 'receiver', 'created_at', 'status']

    def validate_receiver_id(self, value):
        """
        Ensure that a user cannot send a friend request to themselves.
        """
        user = self.context['request'].user
        if user == value:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")
        return value

    def validate(self, attrs):
        """
        Ensure that a friend request does not already exist and users are not already friends.
        """
        user = self.context['request'].user
        receiver = attrs.get('receiver')

        # Check if a pending friend request already exists
        if FriendRequest.objects.filter(
            sender=user,
            receiver=receiver,
            status=FriendRequest.Status.PENDING
        ).exists():
            raise serializers.ValidationError("A pending friend request already exists.")

        # Check if users are already friends
        if Friendship.objects.filter(
            Q(user1=user, user2=receiver) |
            Q(user1=receiver, user2=user)
        ).exists():
            raise serializers.ValidationError("You are already friends with this user.")

        # Check if either user has blocked the other
        if Block.objects.filter(
            Q(blocker=user, blocked=receiver) |
            Q(blocker=receiver, blocked=user)
        ).exists():
            raise serializers.ValidationError("Cannot send a friend request to a blocked user.")

        return attrs

    def create(self, validated_data):
        """
        Override the create method to set the sender to the authenticated user.
        """
        receiver = validated_data.pop('receiver')
        return FriendRequest.objects.create(
            sender=self.context['request'].user,
            receiver=receiver,
            **validated_data
        )


class FriendshipSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ['id', 'user1', 'user2', 'created_at']
        read_only_fields = ['id', 'user1', 'user2', 'created_at']


class BlockSerializer(serializers.ModelSerializer):
    blocker = UserSerializer(read_only=True)
    blocked = UserSerializer(read_only=True)
    blocked_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source='blocked'
    )

    class Meta:
        model = Block
        fields = ['id', 'blocker', 'blocked', 'blocked_id', 'created_at']
        read_only_fields = ['id', 'blocker', 'blocked', 'created_at']

    def validate_blocked_id(self, value):
        """
        Ensure that a user cannot block themselves.
        """
        user = self.context['request'].user
        if user == value:
            raise serializers.ValidationError("You cannot block yourself.")
        return value

    def validate(self, attrs):
        """
        Ensure that a block does not already exist.
        """
        user = self.context['request'].user
        blocked = attrs.get('blocked')

        if Block.objects.filter(blocker=user, blocked=blocked).exists():
            raise serializers.ValidationError("You have already blocked this user.")

        return attrs

    def create(self, validated_data):
        """
        Override the create method to set the blocker to the authenticated user.
        """
        blocked = validated_data.pop('blocked')
        return Block.objects.create(
            blocker=self.context['request'].user,
            blocked=blocked,
            **validated_data
        )
