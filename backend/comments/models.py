# backend/comments/models.py
from datetime import timezone

from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import BaseModel, UUIDModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from tagging.models import TaggedItem

# Get the custom User model
User = get_user_model()


class Comment(UUIDModel, BaseModel):
    """
    Represents a comment made by a user on any content.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="User who made the comment"
    )
    # Generic relation to any content type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    content = models.TextField(help_text="Content of the comment")
    tags = GenericRelation(TaggedItem, related_query_name='comments')

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.content_object}"

    # def save(self, *args, **kwargs):
    #     """
    #     Override save method to automatically update the `updated_at` field on every update.
    #     """
    #     self.updated_at = timezone.now()  # Update the timestamp
    #     return super().save(*args, **kwargs)
