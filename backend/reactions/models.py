from django.db import models
from core.models.base_models import BaseModel, SoftDeleteModel, UUIDModel


class Reaction(BaseModel, SoftDeleteModel, UUIDModel):
    """
    Stores a reaction (emoji) made by a user on different types of items (e.g., Posts, Comments).
    Utilizes PostgreSQL for data consistency and relational query handling.
    """

    # Define available emoji choices for reactions
    EMOJI_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]

    user_id = models.IntegerField(default=0, help_text="ID of the user who reacted")
    user_username = models.CharField(max_length=150, default="unknown", help_text="Username of the user who reacted")
    reacted_item_type = models.CharField(max_length=100, default="unknown", help_text="Type of the item reacted to (e.g., Post, Comment)")
    reacted_item_id = models.CharField(max_length=255, default="0", help_text="ID of the item reacted to")
    emoji = models.CharField(max_length=10, choices=EMOJI_CHOICES, default='like', help_text="Emoji used for the reaction")

    class Meta:
        unique_together = ('user_id', 'reacted_item_type', 'reacted_item_id', 'emoji')
        verbose_name = 'Reaction'
        verbose_name_plural = 'Reactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_username} reacted with {self.emoji} on {self.reacted_item_type} {self.reacted_item_id}"
