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
    # New fields for media, is_active, and viewed_by
    media_type = serializers.ChoiceField(choices=['image', 'video', 'text'], required=False)
    media_url = serializers.URLField(required=False, allow_null=True)
    is_active = serializers.BooleanField(read_only=True)  # Only server can modify is_active
    viewed_by = serializers.ListField(
        child=serializers.IntegerField(),
        read_only=True  # Viewed_by list should be managed internally, not by the user
    )

    class Meta:
        model = Story
        fields = [
            'id', 'user_id', 'user_username', 'content', 'media_type', 'media_url',
            'is_active', 'viewed_by', 'created_at', 'updated_at', 'tags', 'tagged_user_ids'
        ]
        read_only_fields = ['id', 'user_id', 'user_username', 'is_active', 'viewed_by', 'created_at', 'updated_at', 'tags']

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
        # Update the Story instance with validated data
        instance = super().update(instance, validated_data)
        if tagged_user_ids is not None:
            # Remove existing tags and add new ones
            TaggedItem.objects.using('tags_db').filter(tagged_item_type='Story',
                                                       tagged_item_id=str(instance.id)).delete()
            self.create_tagged_items(instance, tagged_user_ids)
        return instance

    def create_tagged_items(self, story, tagged_user_ids):
        """
        Create tagging entries for the story.
        """
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
