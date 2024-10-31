from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import TaggedItem

class TaggedItemSerializer(serializers.ModelSerializer):
    tagged_user = serializers.SerializerMethodField()
    tagged_by = serializers.SerializerMethodField()
    content_object = serializers.SerializerMethodField()

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
        fields = ['id', 'tagged_user', 'tagged_by', 'content_type', 'object_id', 'content_object']
        # Removed 'timestamp' from fields list since it is not in the model
