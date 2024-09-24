from rest_framework import serializers
from .models import Post, PostImage, Tag, Rating
from tagging.serializers import TaggedItemSerializer
from django.contrib.auth import get_user_model
from tagging.models import TaggedItem
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'value', 'user']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    # Explicit handling for file upload and integer fields
    image_files = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=True,
                                     use_url=False),
        write_only=True,
        required=False,
        allow_null=True,
        allow_empty=True
    )

    user_tags = TaggedItemSerializer(many=True, read_only=True)
    tagged_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_null=True,
        allow_empty=True
    )

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'created_at', 'updated_at', 'tags',
            'author', 'images', 'ratings', 'image_files', 'user_tags', 'tagged_user_ids'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'user_tags']

    def validate_image_files(self, value):
        # Validate that each entry in the list is an image
        if value:
            return [v for v in value if v and hasattr(v, 'file')]
        return value

    def validate_tagged_user_ids(self, value):
        # Ensure all IDs are integers and filter out any non-integer values
        if value:
            return [int(v) for v in value if isinstance(v, int) or v.isdigit()]
        return value

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        image_files = validated_data.pop('image_files', [])

        post = Post.objects.create(**validated_data)

        for image_file in image_files:
            if image_file:
                PostImage.objects.create(post=post, image=image_file)

        self.create_tagged_items(post, tagged_user_ids)
        return post

    def create_tagged_items(self, post, tagged_user_ids):
        for user_id in tagged_user_ids:
            TaggedItem.objects.create(
                content_object=post,
                tagged_user_id=user_id,
                tagged_by=self.context['request'].user
            )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.context['request']})
        return context
