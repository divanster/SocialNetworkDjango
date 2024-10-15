# comments/models.py

from django.db import models
from core.models.base_models import BaseModel


class Comment(BaseModel):
    user_id = models.IntegerField()
    user_username = models.CharField(max_length=150)
    post_id = models.UUIDField(null=True, blank=True)
    post_title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(default='No content')
    tags = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.content[:20]
