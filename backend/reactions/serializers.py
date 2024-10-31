from rest_framework import serializers
from .models import Reaction
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field


class ReactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Reaction model.
    Handles serialization and deserialization of data for creating, updating,
    and displaying reactions.
    """
    # Represent content_type as a string instead of ContentType instance
    content_type = serializers.CharField(write_only=True)
    object_id = serializers.CharField()
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

    def create(self, validated_data):
        """
        Override the create method to handle content_type as a string.
        """
        # Convert the string content_type to a ContentType object
        content_type_str = validated_data.pop('content_type')
        try:
            content_type = ContentType.objects.get(model=content_type_str.lower())
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Invalid content type provided.")

        validated_data['content_type'] = content_type
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Override the update method to handle content_type changes.
        """
        content_type_str = validated_data.get('content_type', None)
        if content_type_str:
            try:
                content_type = ContentType.objects.get(model=content_type_str.lower())
                validated_data['content_type'] = content_type
            except ContentType.DoesNotExist:
                raise serializers.ValidationError("Invalid content type provided.")

        return super().update(instance, validated_data)
