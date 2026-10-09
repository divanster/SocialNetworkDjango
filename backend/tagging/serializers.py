from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TaggedItem

User = get_user_model()


class TaggedItemSerializer(serializers.ModelSerializer):
    tagged_user = serializers.SerializerMethodField()
    tagged_by = serializers.SerializerMethodField()
    content_object = serializers.SerializerMethodField()
    tagged_user_id = serializers.PrimaryKeyRelatedField(
        source='tagged_user',
        queryset=User.objects.all(),
        write_only=True
    )

    @extend_schema_field(dict)  # Annotate return type
    def get_tagged_user(self, obj) -> dict:
        from users.serializers import CustomUserSerializer
        return CustomUserSerializer(obj.tagged_user).data

    @extend_schema_field(dict)  # Annotate return type
    def get_tagged_by(self, obj) -> dict:
        from users.serializers import CustomUserSerializer
        return CustomUserSerializer(obj.tagged_by).data

    @extend_schema_field(str)  # Annotate return type
    def get_content_object(self, obj) -> str:
        return str(obj.content_object)

    class Meta:
        model = TaggedItem
        fields = [
            'id', 'tagged_user', 'tagged_by', 'tagged_user_id',
            'content_type', 'object_id', 'content_object'
        ]
        read_only_fields = ['id', 'tagged_user', 'tagged_by', 'content_object']

    def validate(self, attrs):
        content_type = attrs.get('content_type')
        object_id = attrs.get('object_id')
        tagged_user = attrs.get('tagged_user')
        tagged_by = self.context['request'].user

        if tagged_user == tagged_by:
            raise serializers.ValidationError("You cannot tag yourself.")

        if content_type.model not in {'post', 'album', 'photo', 'story'}:
            raise serializers.ValidationError("Tagging is not supported for this content type.")

        model_class = content_type.model_class()
        if model_class is None:
            raise serializers.ValidationError("Invalid content type.")
        if not model_class.objects.filter(id=object_id).exists():
            raise serializers.ValidationError("Target object does not exist.")

        if TaggedItem.objects.filter(
            content_type=content_type,
            object_id=object_id,
            tagged_user=tagged_user
        ).exists():
            raise serializers.ValidationError("This user is already tagged on this object.")

        return attrs
