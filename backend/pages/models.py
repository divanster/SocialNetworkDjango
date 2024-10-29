from django.db import models
from core.models.base_models import BaseModel, UUIDModel
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class Page(UUIDModel, BaseModel):
    """
    Page model to store user-created pages.
    Uses PostgreSQL for efficient storage and relational integrity.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pages',
        help_text="User who created the page"
    )
    title = models.CharField(max_length=255, help_text="Title of the page")
    content = models.TextField(help_text="Content of the page", blank=True)

    class Meta:
        db_table = 'pages'  # Table name in the database
        ordering = ['-created_at']  # Ordering pages by the most recent
        indexes = [
            models.Index(fields=['user']),  # Index for efficient querying by user
            models.Index(fields=['title']),  # Index for efficient querying by title
        ]

    def __str__(self):
        return self.title
