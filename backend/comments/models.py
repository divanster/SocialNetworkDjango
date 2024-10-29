# backend/comments/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models.base_models import BaseModel, UUIDModel

# Get the custom User model
User = get_user_model()


class Comment(UUIDModel, BaseModel):
    """
    Represents a comment made by a user on a post.
    Stored in PostgreSQL as a relational model.
    Inherits from UUIDModel (for primary key), and BaseModel (for created_at and updated_at fields).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="User who made the comment"
    )
    post = models.ForeignKey(
        'social.Post',
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True,
        help_text="The post that the comment is associated with"
    )
    content = models.TextField(default='No content', help_text="Content of the comment")
    tags = models.JSONField(default=list,
                            help_text="List of tags associated with the comment")

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'post', 'created_at']),
        ]

    def __str__(self):
        return self.content[:20]

    def save(self, *args, **kwargs):
        """
        Override save method to automatically update the `updated_at` field on every update.
        """
        self.updated_at = timezone.now()  # Update the timestamp
        return super().save(*args, **kwargs)
