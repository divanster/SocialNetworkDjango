# tagging/models.py

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models.base_models import UUIDModel, BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class TaggedItem(UUIDModel, BaseModel):
    """
    Represents a tagging instance where a user is tagged in any content.
    Uses GenericForeignKey to link to any model instance.
    """
    # Generic foreign key to any content type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Information about the tagged user
    tagged_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tags_received',
        help_text="User being tagged"
    )

    # Information about who tagged the user
    tagged_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tags_created',
        help_text="User who tagged another user"
    )

    class Meta:
        unique_together = ('content_type', 'object_id', 'tagged_user')
        ordering = ['-created_at']
        verbose_name = 'Tagged Item'
        verbose_name_plural = 'Tagged Items'

    def __str__(self):
        return f"{self.tagged_by.username} tagged {self.tagged_user.username} in {self.content_object}"
