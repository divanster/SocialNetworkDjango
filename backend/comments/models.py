# backend/comments/models.py

from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import BaseModel, UUIDModel, SoftDeleteModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from tagging.models import TaggedItem
from django.utils import timezone  # Correct import for timezone

# Get the custom User model
User = get_user_model()


class Comment(UUIDModel, BaseModel, SoftDeleteModel):
    """
    Represents a comment made by a user on any content.
    Inherits from UUIDModel, BaseModel, and SoftDeleteModel to utilize UUIDs, timestamps, and soft deletion.
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

    # Removed unnecessary save method since BaseModel handles updated_at via auto_now=True

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
