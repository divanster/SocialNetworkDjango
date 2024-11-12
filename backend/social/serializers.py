from rest_framework import serializers
from social.models import Post, PostImage, Rating
from tagging.models import TaggedItem
from drf_spectacular.utils import extend_schema_field
import logging
from django.contrib.auth import get_user_model
from core.choices import VisibilityChoices

User = get_user_model()

logger = logging.getLogger(__name__)


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )
    image_files = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    average_rating = serializers.ReadOnlyField()

    # Use ChoiceField for visibility, automatically handles validation
    visibility = serializers.ChoiceField(choices=VisibilityChoices.choices)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'visibility', 'created_at',
                  'updated_at', 'tags', 'tagged_user_ids', 'image_files',
                  'average_rating']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'tags',
                            'average_rating']

    @extend_schema_field(serializers.ListSerializer(child=serializers.DictField()))
    def get_tags(self, obj):
        """
        Get a list of tagged users associated with the post.
        """
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
        Create a new post along with the associated tagged users and images.
        """
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        image_files = validated_data.pop('image_files', [])
        post = Post.objects.create(**validated_data)

        # Create the associated tagged items
        self.create_tagged_items(post, tagged_user_ids)

        # Create post images
        self.create_post_images(post, image_files)

        logger.info(
            f"[SERIALIZER] Post with ID {post.id} created and tagged users added.")
        return post

    def update(self, instance, validated_data):
        """
        Update an existing post, updating its tags and images if necessary.
        """
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        image_files = validated_data.pop('image_files', [])
        post = super().update(instance, validated_data)

        # Update tags if tagged_user_ids is provided
        if tagged_user_ids is not None:
            instance.tags.all().delete()
            self.create_tagged_items(post, tagged_user_ids)
            logger.info(f"[SERIALIZER] Tags updated for post with ID {post.id}.")

        # Create new images if provided
        if image_files:
            self.create_post_images(post, image_files)

        return post

    def create_tagged_items(self, post, tagged_user_ids):
        """
        Create tagged items for users who are tagged in the post.
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

    def create_post_images(self, post, image_files):
        """
        Create PostImage entries for the provided image files.
        """
        for image in image_files:
            try:
                PostImage.objects.create(post=post, image=image)
                logger.info(f"[SERIALIZER] Image uploaded for post {post.id}.")
            except Exception as e:
                logger.warning(
                    f"[SERIALIZER] Failed to upload image for post {post.id}: {e}")


class RatingSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing ratings related to posts.
    """
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(),
                                                 source='post')
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                                 source='user')

    class Meta:
        model = Rating
        fields = ['post_id', 'user_id', 'value']

    def validate_value(self, value):
        """
        Validate the rating value is between 1 and 5.
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        """
        Create a new rating.
        """
        rating = Rating.objects.create(**validated_data)
        logger.info(
            f"[SERIALIZER] Rating created for post {rating.post.id} by user {rating.user.username}.")
        return rating

    def update(self, instance, validated_data):
        """
        Update an existing rating.
        """
        instance.value = validated_data.get('value', instance.value)
        instance.save()
        logger.info(
            f"[SERIALIZER] Rating updated for post {instance.post.id} by user {instance.user.username}.")
        return instance
