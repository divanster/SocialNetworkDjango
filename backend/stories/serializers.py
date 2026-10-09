from rest_framework import serializers
from .models import Story
from tagging.models import TaggedItem
from core.choices import VisibilityChoices
from drf_spectacular.utils import extend_schema_field
import logging
from uuid import uuid4

from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class StorySerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField(
        source='user', read_only=True, help_text="Username of the story author"
    )  # Fetch user username
    tags = serializers.SerializerMethodField()  # To display tags information
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False,
        help_text="IDs of users to tag in the story"
    )
    media_file = serializers.FileField(write_only=True, required=False)
    media_type = serializers.ChoiceField(
        choices=Story.MEDIA_TYPE_CHOICES,
        required=False,
        help_text="Type of media content"
    )
    visibility = serializers.ChoiceField(
        choices=VisibilityChoices.choices,
        required=False,
        help_text="Story visibility setting"
    )

    class Meta:
        model = Story
        fields = [
            'id', 'user', 'user_name', 'content', 'media_type', 'media_url',
            'is_active', 'viewed_by', 'created_at', 'updated_at', 'tags',
            'tagged_user_ids', 'visibility', 'media_file'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'is_active', 'viewed_by',
            'created_at', 'updated_at', 'tags'
        ]

    @extend_schema_field(serializers.ListSerializer(child=serializers.DictField()))
    def get_tags(self, obj):
        """
        Retrieve tags associated with the story.
        """
        tags = TaggedItem.objects.filter(object_id=obj.id, content_type__model='story')
        return [
            {
                'tagged_user_id': tag.tagged_user_id,
                'tagged_user_username': tag.tagged_user.username if tag.tagged_user else None
            }
            for tag in tags
        ]

    def create(self, validated_data):
        """
        Create a story instance, along with tagging information.
        """
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        media_file = validated_data.pop('media_file', None)
        self._attach_media_file(validated_data, media_file)
        story = Story.objects.create(**validated_data)
        self.create_tagged_items(story, tagged_user_ids)
        return story

    def update(self, instance, validated_data):
        """
        Update a story instance and handle updating tagged items.
        """
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        media_file = validated_data.pop('media_file', None)
        self._attach_media_file(validated_data, media_file)
        instance = super().update(instance, validated_data)
        if tagged_user_ids is not None:
            # Remove all existing tags for the story
            TaggedItem.objects.filter(object_id=instance.id, content_type__model='story').delete()
            # Recreate tagged items
            self.create_tagged_items(instance, tagged_user_ids)
        return instance

    def validate(self, attrs):
        content = attrs.get('content', getattr(self.instance, 'content', None))
        media_url = attrs.get('media_url', getattr(self.instance, 'media_url', None))
        media_file = attrs.get('media_file')
        if not content and not media_url and not media_file:
            raise serializers.ValidationError("Story requires content or media.")
        return attrs

    def _attach_media_file(self, validated_data, media_file):
        if not media_file:
            return

        user = self.context['request'].user
        saved_path = default_storage.save(f"stories/{user.id}/{uuid4()}_{media_file.name}", media_file)
        media_url = default_storage.url(saved_path)
        request = self.context.get('request')
        validated_data['media_url'] = request.build_absolute_uri(media_url) if request else media_url

        media_type = validated_data.get('media_type')
        if media_type:
            return
        content_type = getattr(media_file, 'content_type', '') or ''
        validated_data['media_type'] = 'video' if content_type.startswith('video/') else 'image'

    def create_tagged_items(self, story, tagged_user_ids):
        """
        Create tagged items for the story.
        """
        tagged_by = self.context['request'].user  # Get the user creating the story
        for user_id in tagged_user_ids:
            try:
                TaggedItem.objects.create(
                    content_object=story,
                    tagged_user_id=user_id,
                    tagged_by=tagged_by
                )
                logger.info(f"User {user_id} successfully tagged in story {story.id}.")
            except Exception as e:
                logger.warning(f"Failed to tag user {user_id} in story {story.id}: {e}")
