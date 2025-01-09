# backend/follows/models.py

from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import SoftDeleteModel, BaseModel  # Ensure SoftDeleteModel is imported

# Get the custom User model
User = get_user_model()


# Follow model to store follow relationships between users
class Follow(SoftDeleteModel, BaseModel):
    # ForeignKey relationships to track followers and followings
    follower = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE
    )

    # Meta class to define unique constraints
    class Meta:
        unique_together = ('follower', 'followed')
        verbose_name = 'Follow Relationship'
        verbose_name_plural = 'Follow Relationships'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('followed')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
