from rest_framework import serializers
from .models import Post, Tag, Rating
from comments.serializers import CommentSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RatingSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'post', 'value']
        read_only_fields = ['id', 'user', 'post']


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'tags', 'average_rating', 'image', 'author']
        read_only_fields = ['id', 'average_rating']

    @staticmethod
    def _get_or_create_tags(tags, post):
        tag_objects = []
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(name=tag['name'])
            tag_objects.append(tag_obj)
        post.tags.set(tag_objects)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        post.author = self.context['request'].user
        post.save()
        self._get_or_create_tags(tags, post)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            self._get_or_create_tags(tags, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PostDetailSerializer(PostSerializer):
    ratings = RatingSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['ratings', 'comments']


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
