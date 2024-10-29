from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import UUIDModel, BaseModel
from django.contrib.contenttypes.fields import GenericRelation
from tagging.models import TaggedItem

# Get the custom User model
User = get_user_model()


class Story(UUIDModel, BaseModel):
    """
    Represents a user's story, including text, image, or video content.
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
    viewed_by = models.ManyToManyField(
        User,
        related_name='viewed_stories',
        blank=True,
        help_text="Users who have viewed the story"
    )
    # GenericRelation to use tags
    tags = GenericRelation(TaggedItem, related_query_name='stories')

    class Meta:
        db_table = 'stories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),  # Index for efficient user-based querying
            models.Index(fields=['created_at']),  # Index for story ordering by date
        ]

    def __str__(self):
        return f"Story by {self.user.username} at {self.created_at}"

    def deactivate_story(self):
        """
        Mark the story as inactive after the expiration period.
        """
        self.is_active = False
        self.save()

    def add_view(self, user):
        """
        Add a user to the list of users who have viewed the story.
        """
        self.viewed_by.add(user)
