from django.db import models
from core.models.base_models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Story(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    content = models.TextField()

    def __str__(self):
        return f"Story by {self.user.username} at {self.created_at}"
