from rest_framework import serializers
from .models import Post, PostImage, Tag, Rating


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

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'tags',
                  'author', 'images', 'ratings', 'image_files']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        post = Post.objects.create(**validated_data)
        try:
            for image_file in image_files:
                PostImage.objects.create(post=post, image=image_file)
        except Exception as e:
            post.delete()  # Delete the post if image saving fails
            raise serializers.ValidationError(
                f"An error occurred while saving images: {e}")
        return post
