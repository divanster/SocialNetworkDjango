# backend/stories/base_models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Story by {self.user.username} at {self.created_at}"
