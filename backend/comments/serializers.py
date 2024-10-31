from rest_framework import serializers
from .models import Comment
from tagging.serializers import TaggedItemSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from users.serializers import CustomUserSerializer
User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    # Adding fields for tags and tagging
    tags = TaggedItemSerializer(many=True, read_only=True)
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False,
        help_text="List of user UUIDs to tag in the comment."
    )
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'content', 'content_type', 'object_id', 'created_at',
            'updated_at', 'tags',
            'tagged_user_ids'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'tags']

    @extend_schema_field(CustomUserSerializer)  # Adding the schema field annotation
    def get_user(self, obj) -> dict:
        return CustomUserSerializer(obj.user).data

    def create(self, validated_data):
        # Extract `tagged_user_ids` from the validated data
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])

        # Create the comment instance
        comment = Comment.objects.create(**validated_data)

        # Create tagging information if tagged users are provided
        self.create_tagged_items(comment, tagged_user_ids)
        return comment

    def update(self, instance, validated_data):
        # Extract `tagged_user_ids` from the validated data
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)

        # Perform the base update with the validated data
        comment = super().update(instance, validated_data)

        # Update tagging information if `tagged_user_ids` are provided
        if tagged_user_ids is not None:
            # Remove all existing tags for this comment
            instance.tags.all().delete()

            # Create new tagging items
            self.create_tagged_items(comment, tagged_user_ids)

        return comment

    def create_tagged_items(self, comment, tagged_user_ids):
        """
        Helper method to create TaggedItem instances for the comment.
        """
        from tagging.models import TaggedItem
        request = self.context.get('request')
        tagged_by = request.user if request and hasattr(request, 'user') else None

        for user_id in tagged_user_ids:
            try:
                tagged_user = User.objects.get(id=user_id)
                TaggedItem.objects.create(
                    content_object=comment,
                    tagged_user=tagged_user,
                    tagged_by=tagged_by
                )
            except User.DoesNotExist:
                # Log warning and skip if user does not exist
                continue  # You could add logging here for better tracking
