# reactions/models.py

from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import UUIDModel, BaseModel, SoftDeleteModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class Reaction(UUIDModel, BaseModel, SoftDeleteModel):
    """
    Stores a reaction (emoji) made by a user on different types of items.
    """
    EMOJI_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reactions',
        help_text="User who reacted"
    )
    # Generic relation to any content type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    emoji = models.CharField(
        max_length=10,
        choices=EMOJI_CHOICES,
        default='like',
        help_text="Emoji used for the reaction"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id', 'emoji'],
                name='unique_user_content_reaction'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} reacted with {self.emoji} on {self.content_object}"
