from rest_framework import serializers
from .models import Comment
from tagging.serializers import TaggedItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    # Adding fields for tags and tagging
    tags = TaggedItemSerializer(many=True, read_only=True)
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at', 'updated_at', 'tags',
                  'tagged_user_ids']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'tags']

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        comment = Comment.objects.create(**validated_data)
        self.create_tagged_items(comment, tagged_user_ids)
        return comment

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        comment = super().update(instance, validated_data)

        # Update tags if needed
        if tagged_user_ids is not None:
            instance.tags.all().delete()
            self.create_tagged_items(comment, tagged_user_ids)

        return comment

    def create_tagged_items(self, comment, tagged_user_ids):
        from tagging.models import TaggedItem
        request = self.context.get('request')
        tagged_by = request.user if request and hasattr(request, 'user') else None

        for user_id in tagged_user_ids:
            try:
                tagged_user = User.objects.get(id=user_id)
                TaggedItem.objects.create(content_object=comment,
                                          tagged_user=tagged_user, tagged_by=tagged_by)
            except User.DoesNotExist:
                continue  # Skip if user does not exist
