from rest_framework import serializers
from social.models import Post
from tagging.models import TaggedItem
from drf_spectacular.utils import extend_schema_field
import logging

logger = logging.getLogger(__name__)


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )
    user = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'user', 'visibility', 'created_at',
                  'updated_at', 'tags', 'tagged_user_ids']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'tags']

    @extend_schema_field(serializers.ListSerializer(child=serializers.DictField()))
    def get_tags(self, obj):
        # Changed obj.uuid to obj.id
        tags = TaggedItem.objects.filter(object_id=obj.id, content_type__model='post')
        return [
            {
                'tagged_user_id': tag.tagged_user_id,
                'tagged_user_username': tag.tagged_user.username if tag.tagged_user else None
            }
            for tag in tags
        ]

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        post = Post.objects.create(**validated_data)
        self.create_tagged_items(post, tagged_user_ids)
        logger.info(
            f"[SERIALIZER] Post with ID {post.id} created and tagged users added.")  # Changed uuid to id
        return post

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        post = super().update(instance, validated_data)

        if tagged_user_ids is not None:
            instance.tags.all().delete()
            self.create_tagged_items(post, tagged_user_ids)
            logger.info(
                f"[SERIALIZER] Tags updated for post with ID {post.id}.")  # Changed uuid to id

        return post

    def create_tagged_items(self, post, tagged_user_ids):
        tagged_by = self.context['request'].user
        for user_id in tagged_user_ids:
            try:
                TaggedItem.objects.create(
                    content_object=post,
                    tagged_user_id=user_id,
                    tagged_by=tagged_by
                )
                logger.info(
                    f"[SERIALIZER] User {user_id} tagged in post {post.id}.")  # Changed uuid to id
            except Exception as e:
                logger.warning(
                    f"[SERIALIZER] Failed to tag user {user_id} in post {post.id}: {e}")  # Changed uuid to id
