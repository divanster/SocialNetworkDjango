from django.db import models
from core.models.base_models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Page(BaseModel):
    user = models.ForeignKey(User, related_name='pages', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title
