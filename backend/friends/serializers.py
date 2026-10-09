from rest_framework import serializers
from .models import FriendRequest, Friendship, Block
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'profile_picture']

    def get_full_name(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile:
            full_name = f"{profile.first_name} {profile.last_name}".strip()
            if full_name:
                return full_name
        return obj.username

    def get_profile_picture(self, obj):
        profile = getattr(obj, 'profile', None)
        if not profile or not profile.profile_picture:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(profile.profile_picture.url)
        return profile.profile_picture.url


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

        # If the receiver already sent a pending request, avoid creating the opposite duplicate.
        if FriendRequest.objects.filter(
            sender=receiver,
            receiver=user,
            status=FriendRequest.Status.PENDING
        ).exists():
            raise serializers.ValidationError("This user has already sent you a friend request.")

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
        sender = self.context['request'].user
        receiver = validated_data.pop('receiver')
        existing = FriendRequest.all_objects.filter(sender=sender, receiver=receiver).first()
        if existing:
            existing.status = FriendRequest.Status.PENDING
            existing.is_deleted = False
            existing.deleted_at = None
            existing.save(update_fields=['status', 'is_deleted', 'deleted_at'])
            return existing

        return FriendRequest.objects.create(sender=sender, receiver=receiver, **validated_data)


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
