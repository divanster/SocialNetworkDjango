# backend/pages/base_models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Page(models.Model):
    user = models.ForeignKey(User, related_name='pages', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
