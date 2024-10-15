from django.db import models
from core.models.base_models import BaseModel


class Page(BaseModel):
    user_id = models.IntegerField()
    user_username = models.CharField(max_length=150)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title
