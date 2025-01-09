# backend/stories/models.py
import logging

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from core.models.base_models import BaseModel, UUIDModel, SoftDeleteModel
from tagging.models import TaggedItem
from core.choices import VisibilityChoices  # Import visibility choices
from django.utils import timezone  # Correct import for timezone

User = get_user_model()


def get_friends(user):
    from friends.models import Friendship
    friends = Friendship.objects.filter(
        models.Q(user1=user) | models.Q(user2=user)
    )
    friend_ids = set()
    for friendship in friends:
        friend_ids.add(friendship.user1_id)
        friend_ids.add(friendship.user2_id)
    friend_ids.discard(user.id)
    return User.objects.filter(id__in=friend_ids)


class StoryQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if user.is_anonymous:
            return self.filter(visibility=VisibilityChoices.PUBLIC, is_active=True, is_deleted=False)
        else:
            public_stories = self.filter(
                visibility=VisibilityChoices.PUBLIC,
                is_active=True,
                is_deleted=False
            )
            friends_stories = self.filter(
                visibility=VisibilityChoices.FRIENDS,
                user__in=get_friends(user),
                is_active=True,
                is_deleted=False
            )
            own_stories = self.filter(user=user, is_deleted=False)
            return public_stories | friends_stories | own_stories


class StoryManager(models.Manager):
    def get_queryset(self):
        return StoryQuerySet(self.model, using=self._db)

    def visible_to_user(self, user):
        return self.get_queryset().visible_to_user(user)


class Story(UUIDModel, BaseModel, SoftDeleteModel):
    """
    Represents a user's story, which can include text, images, or videos.
    Inherits from UUIDModel, BaseModel, and SoftDeleteModel to utilize UUIDs, timestamps, and soft deletion.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stories',
        help_text="User who created the story"
    )
    content = models.TextField(
        help_text="Text content of the story. Can be short and engaging.",
        blank=True,
        null=True
    )
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text'),
    ]
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default='text',
        help_text="Type of media content for the story"
    )
    media_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        help_text="URL of the media associated with the story"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether the story is active (visible to others)"
    )
    visibility = models.CharField(
        max_length=10,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.FRIENDS,
        help_text="Visibility of the story"
    )
    viewed_by = models.ManyToManyField(
        User,
        related_name='viewed_stories',
        blank=True,
        help_text="Users who have viewed the story"
    )
    tags = GenericRelation(TaggedItem, related_query_name='stories')

    objects = StoryManager()  # Use custom manager

    class Meta:
        db_table = 'stories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['visibility']),
        ]

    def __str__(self):
        return f"Story by {self.user.username} at {self.created_at}"

    def deactivate_story(self):
        """
        Mark the story as inactive after the expiration period.
        """
        self.is_active = False
        self.save()
        logger = logging.getLogger(__name__)
        logger.info(f"Story with ID {self.id} has been deactivated.")

    def add_view(self, user):
        """
        Add a user to the list of those who have viewed the story.
        """
        self.viewed_by.add(user)
        logger = logging.getLogger(__name__)
        logger.info(f"User {user.id} viewed Story {self.id}.")

    def _cascade_soft_delete(self):
        """
        Override this method in subclasses to perform cascading soft deletes.
        Currently, there are no related objects to cascade.
        """
        pass

    def _cascade_restore(self):
        """
        Override this method in subclasses to perform cascading restores.
        Currently, there are no related objects to restore.
        """
        pass
