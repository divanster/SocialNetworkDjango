# backend/comments/models.py
from django.db import models
from django.contrib.auth import get_user_model
from social.models import Post

User = get_user_model()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)  # Make nullable temporarily
    content = models.TextField(null=True, blank=True)  # Also make content nullable
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:20]
