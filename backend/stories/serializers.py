# backend/stories/serializers.py

from rest_framework import serializers
from .models import Story
from tagging.serializers import TaggedItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class StorySerializer(serializers.ModelSerializer):
    tags = TaggedItemSerializer(many=True, read_only=True)
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )

    class Meta:
        model = Story
        fields = [
            'id', 'user', 'content', 'created_at', 'updated_at', 'tags',
            'tagged_user_ids'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'tags']

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        story = Story.objects.create(**validated_data)
        self.create_tagged_items(story, tagged_user_ids)
        return story

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        story = super().update(instance, validated_data)
        if tagged_user_ids is not None:
            # Remove existing tags and add new ones
            instance.tags.all().delete()
            self.create_tagged_items(story, tagged_user_ids)
        return story

    def create_tagged_items(self, story, tagged_user_ids):
        from tagging.models import TaggedItem
        for user_id in tagged_user_ids:
            TaggedItem.objects.create(
                content_object=story,
                tagged_user_id=user_id,
                tagged_by=self.context['request'].user
            )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.context['request']})
        return context
