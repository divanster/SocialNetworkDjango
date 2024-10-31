# backend/social/serializers.py

from rest_framework import serializers
from social.models import Post
from tagging.models import TaggedItem
import logging

logger = logging.getLogger(__name__)


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()  # Fetching tags for display
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'visibility', 'created_at',
                  'updated_at', 'tags', 'tagged_user_ids']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'tags']

    def get_tags(self, obj):
        # Retrieve tags associated with the post
        tags = TaggedItem.objects.filter(object_id=obj.id, content_type__model='post')
        return [
            {
                'tagged_user_id': tag.tagged_user_id,
                'tagged_user_username': tag.tagged_user.username if tag.tagged_user else None
            }
            for tag in tags
        ]

    def create(self, validated_data):
        """
        Create a post instance and create tagged items for tagged users.
        """
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        post = Post.objects.create(**validated_data)

        # Create tagged items for the new post
        self.create_tagged_items(post, tagged_user_ids)
        logger.info(
            f"[SERIALIZER] Post with ID {post.id} created and tagged users added.")

        return post

    def update(self, instance, validated_data):
        """
        Update a post instance and handle updating tagged items.
        """
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        post = super().update(instance, validated_data)

        if tagged_user_ids is not None:
            # Remove all existing tags
            instance.tags.all().delete()
            # Recreate tags with the provided user IDs
            self.create_tagged_items(post, tagged_user_ids)
            logger.info(f"[SERIALIZER] Tags updated for post with ID {post.id}.")

        return post

    def create_tagged_items(self, post, tagged_user_ids):
        """
        Create tagging entries for the post.
        """
        tagged_by = self.context['request'].user
        for user_id in tagged_user_ids:
            try:
                TaggedItem.objects.create(
                    content_object=post,
                    tagged_user_id=user_id,
                    tagged_by=tagged_by
                )
                logger.info(f"[SERIALIZER] User {user_id} tagged in post {post.id}.")
            except Exception as e:
                logger.warning(
                    f"[SERIALIZER] Failed to tag user {user_id} in post {post.id}: {e}")
