from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import BaseModel, UUIDModel
from albums.models import Album, Photo

User = get_user_model()


class TaggedItem(UUIDModel, BaseModel):
    """
    Represents a tagging instance where a user is tagged in an album, photo, or any content.
    Uses direct relationships with the Album, Photo, and User models.
    """

    # Relationships to define the tagged content
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='tagged_items',
        null=True,
        blank=True,
        help_text="Album in which the user is tagged (optional)",
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name='tagged_items',
        null=True,
        blank=True,
        help_text="Photo in which the user is tagged (optional)",
    )

    # Fields to define information about the tagged user
    tagged_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tags_received',
        help_text="User being tagged"
    )

    # Fields to define information about the tagging action
    tagged_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tags_created',
        help_text="User who tagged another user"
    )

    class Meta:
        unique_together = ('album', 'photo', 'tagged_user')
        ordering = ['-created_at']
        verbose_name = 'Tagged Item'
        verbose_name_plural = 'Tagged Items'

    def __str__(self):
        content = self.album if self.album else self.photo
        content_type = "Album" if self.album else "Photo"
        return (
            f"{self.tagged_by.username} tagged {self.tagged_user.username} in "
            f"{content_type} '{content}'"
        )
