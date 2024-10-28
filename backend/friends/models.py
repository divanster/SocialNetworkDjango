# backend/friends/models.py

from django.core.exceptions import ValidationError
from django.db import models
from core.models.base_models import BaseModel


# FriendRequest model to manage friend requests between users
class FriendRequest(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    sender_id = models.IntegerField(default=0)  # Default value to handle existing rows
    sender_username = models.CharField(max_length=150, default="unknown")  # Default value to handle existing rows
    receiver_id = models.IntegerField(default=0)  # Default value to handle existing rows
    receiver_username = models.CharField(max_length=150, default="unknown")  # Default value to handle existing rows
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    class Meta:
        unique_together = ('sender_id', 'receiver_id')
        constraints = [
            models.UniqueConstraint(
                fields=['sender_id', 'receiver_id'],
                condition=models.Q(status='pending'),
                name='unique_pending_request'
            )
        ]
        verbose_name = 'Friend Request'
        verbose_name_plural = 'Friend Requests'

    def __str__(self):
        return f"{self.sender_username} -> {self.receiver_username} ({self.status})"


# Friendship model to manage active friendships
class Friendship(BaseModel):
    user1_id = models.IntegerField(default=0)  # Default value to handle existing rows
    user1_username = models.CharField(max_length=150, default="unknown")  # Default value to handle existing rows
    user2_id = models.IntegerField(default=0)  # Default value to handle existing rows
    user2_username = models.CharField(max_length=150, default="unknown")  # Default value to handle existing rows

    class Meta:
        unique_together = ('user1_id', 'user2_id')
        constraints = [
            models.CheckConstraint(
                check=models.Q(user1_id__lt=models.F('user2_id')),
                name='user1_lt_user2'
            )
        ]
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'

    def __str__(self):
        return f"{self.user1_username} & {self.user2_username}"


# Block model to manage blocking between users
class Block(BaseModel):
    blocker_id = models.IntegerField(default=0)  # Default value to handle existing rows
    blocker_username = models.CharField(max_length=150, default="unknown")  # Default value to handle existing rows
    blocked_id = models.IntegerField(default=0)  # Default value to handle existing rows
    blocked_username = models.CharField(max_length=150, default="unknown")  # Default value to handle existing rows

    class Meta:
        unique_together = ('blocker_id', 'blocked_id')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(blocker_id=models.F('blocked_id')),
                name='block_self_check'
            )
        ]
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'

    def __str__(self):
        return f"{self.blocker_username} blocked {self.blocked_username}"
