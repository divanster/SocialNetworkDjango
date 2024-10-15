# backend/stories/models.py

from django.db import models
from core.models.base_models import BaseModel
from django.core.validators import MinValueValidator


class Story(BaseModel):
    user_id = models.IntegerField(validators=[MinValueValidator(1)],
                                  help_text="ID of the user who created the story")
    user_username = models.CharField(max_length=150,
                                     help_text="Username of the user who created the "
                                               "story")
    content = models.TextField(
        help_text="Content of the story. Keep it short and engaging.")

    def __str__(self):
        return f"Story by {self.user_username} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']  # Ordering the stories by most recent
