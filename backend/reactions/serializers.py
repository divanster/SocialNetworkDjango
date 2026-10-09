from rest_framework import serializers
from .models import Reaction
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from social.models import Post
from comments.models import Comment


class ReactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Reaction model.
    Handles serialization and deserialization of data for creating, updating,
    and displaying reactions.
    """
    # Represent content_type as a string instead of ContentType instance
    content_type = serializers.CharField(write_only=True)
    object_id = serializers.UUIDField()
    user_username = serializers.SerializerMethodField()

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'user_username', 'content_type', 'object_id', 'emoji', 'created_at']
        read_only_fields = ['id', 'user', 'user_username', 'created_at']

    @extend_schema_field(serializers.CharField)
    def get_user_username(self, obj):
        return obj.user.username

    def validate_content_type(self, value):
        """
        Validate that the provided content type exists.
        """
        if not ContentType.objects.filter(model=value.lower()).exists():
            raise serializers.ValidationError("Invalid content type.")
        return value

    def validate(self, attrs):
        content_type_value = attrs.get('content_type')
        object_id = attrs.get('object_id')
        emoji = attrs.get('emoji')

        content_type = ContentType.objects.get(model=content_type_value.lower())
        model_class = content_type.model_class()

        if model_class is None:
            raise serializers.ValidationError("Invalid content type.")
        if model_class not in (Post, Comment):
            raise serializers.ValidationError("Reactions are only supported for posts and comments.")
        if not model_class.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError({"object_id": "Target object not found."})

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and self.instance is None:
            duplicate_exists = Reaction.objects.filter(
                user=user,
                content_type=content_type,
                object_id=object_id,
                emoji=emoji
            ).exists()
            if duplicate_exists:
                raise serializers.ValidationError({"detail": "You have already added this reaction."})

        attrs['content_type'] = content_type
        return attrs

    def create(self, validated_data):
        """
        Override the create method to handle restoration for soft-deleted duplicates.
        """
        existing = Reaction.all_objects.filter(
            user=validated_data['user'],
            content_type=validated_data['content_type'],
            object_id=validated_data['object_id'],
            emoji=validated_data['emoji']
        ).first()

        if existing and existing.is_deleted:
            existing.restore()
            return existing
        if existing:
            raise serializers.ValidationError({"detail": "You have already added this reaction."})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Override the update method to handle content_type changes.
        """
        return super().update(instance, validated_data)
