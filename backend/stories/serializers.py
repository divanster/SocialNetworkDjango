# backend/stories/serializers.py

from rest_framework import serializers
from .models import Story
from tagging.models import TaggedItem
import logging

logger = logging.getLogger(__name__)


class StorySerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    tagged_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Story
        fields = [
            'id', 'user_id', 'user_username', 'content', 'created_at', 'updated_at',
            'tags',
            'tagged_user_ids'
        ]
        read_only_fields = ['id', 'user_id', 'user_username', 'created_at',
                            'updated_at', 'tags']

    def get_tags(self, obj):
        # Get all tags for this story
        tags = TaggedItem.objects.using('tags_db').filter(tagged_item_type='Story',
                                                          tagged_item_id=str(obj.id))
        return [
            {
                'tagged_user_id': tag.tagged_user_id,
                'tagged_user_username': tag.tagged_user_username
            }
            for tag in tags
        ]

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        story = Story.objects.using('stories_db').create(**validated_data)
        self.create_tagged_items(story, tagged_user_ids)
        return story

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        story = super().update(instance, validated_data)
        if tagged_user_ids is not None:
            # Remove existing tags and add new ones
            TaggedItem.objects.using('tags_db').filter(tagged_item_type='Story',
                                                       tagged_item_id=str(
                                                           instance.id)).delete()
            self.create_tagged_items(story, tagged_user_ids)
        return story

    def create_tagged_items(self, story, tagged_user_ids):
        for user_id in tagged_user_ids:
            TaggedItem.objects.using('tags_db').create(
                tagged_item_type='Story',
                tagged_item_id=str(story.id),
                tagged_user_id=user_id,
                tagged_user_username=self.get_user_username(user_id),
                tagged_by_id=self.context['request'].user.id,
                tagged_by_username=self.context['request'].user.username
            )

    def get_user_username(self, user_id):
        """
        Retrieve username based on the user ID from user database.
        Assumes a separate user database is used.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.using('users_db').get(id=user_id)
            return user.username
        except User.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found when tagging story.")
            return 'Unknown'
