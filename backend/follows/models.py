# follows/models.py

from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import BaseModel

User = get_user_model()


class Follow(BaseModel):
    follower = models.ForeignKey(User, related_name='following',
                                 on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers',
                                 on_delete=models.CASCADE)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
