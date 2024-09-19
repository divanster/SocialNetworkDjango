# backend/social/serializers.py

from rest_framework import serializers
from .models import Post, PostImage, Tag, Rating
from tagging.serializers import TaggedItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


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
    image_files = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=True,
                                     use_url=False),
        write_only=True,
        required=False
    )
    user_tags = TaggedItemSerializer(many=True, read_only=True)
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'created_at', 'updated_at', 'tags',
            'author', 'images', 'ratings', 'image_files', 'user_tags', 'tagged_user_ids'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'user_tags']

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        image_files = validated_data.pop('image_files', [])
        post = Post.objects.create(**validated_data)
        try:
            for image_file in image_files:
                PostImage.objects.create(post=post, image=image_file)
            self.create_tagged_items(post, tagged_user_ids)
        except Exception as e:
            post.delete()  # Delete the post if image saving fails
            raise serializers.ValidationError(
                f"An error occurred while saving images: {e}")
        return post

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        image_files = validated_data.pop('image_files', [])
        post = super().update(instance, validated_data)
        if image_files:
            for image_file in image_files:
                PostImage.objects.create(post=post, image=image_file)
        if tagged_user_ids is not None:
            # Remove existing tags and add new ones
            instance.user_tags.all().delete()
            self.create_tagged_items(post, tagged_user_ids)
        return post

    def create_tagged_items(self, post, tagged_user_ids):
        from tagging.models import TaggedItem
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
