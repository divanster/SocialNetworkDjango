# backend/social/serializers.py

import logging
from rest_framework import serializers
from social.models import Post, PostImage, Rating
from tagging.models import TaggedItem
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import ValidationError

# Initialize logger
logger = logging.getLogger(__name__)


class PostImageSerializer(serializers.ModelSerializer):
    """
    Serializer for PostImage model.
    Excludes soft-deletion fields.
    """
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RatingSerializer(serializers.ModelSerializer):
    """
    Serializer for Rating model.
    Excludes soft-deletion fields.
    """
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'value', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model.
    Handles nested PostImage and Rating serializers.
    Manages tagging functionality.
    Excludes soft-deletion fields.
    """
    tags = serializers.SerializerMethodField()
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )
    images = PostImageSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'user', 'visibility', 'created_at',
            'updated_at', 'tags', 'tagged_user_ids', 'images', 'ratings'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'tags', 'images', 'ratings']

    @extend_schema_field(serializers.ListSerializer(child=serializers.DictField()))
    def get_tags(self, obj):
        """
        Retrieves tags associated with the post.
        """
        if hasattr(obj, 'tags'):
            return [
                {
                    'tagged_user_id': str(tag.tagged_user_id),
                    'tagged_user_username': tag.tagged_user.username if tag.tagged_user else None,
                }
                for tag in obj.tags.all()
            ]
        return []

    def create(self, validated_data):
        """
        Creates a Post instance and handles tagging.
        """
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        post = Post.objects.create(**validated_data)
        self.create_tagged_items(post, tagged_user_ids)
        logger.info(f"[SERIALIZER] Post with ID {post.id} created and tagged users added.")
        return post

    def update(self, instance, validated_data):
        """
        Updates a Post instance and handles tagging.
        """
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        post = super().update(instance, validated_data)

        if tagged_user_ids is not None:
            instance.tags.all().delete()
            self.create_tagged_items(post, tagged_user_ids)
            logger.info(f"[SERIALIZER] Tags updated for post with ID {post.id}.")

        return post

    def create_tagged_items(self, post, tagged_user_ids):
        """
        Creates TaggedItem instances for the post.
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
                logger.warning(f"[SERIALIZER] Failed to tag user {user_id} in post {post.id}: {e}")
