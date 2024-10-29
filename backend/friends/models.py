from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import BaseModel

# Get the custom User model
User = get_user_model()


# FriendRequest model to manage friend requests between users
class FriendRequest(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    sender = models.ForeignKey(
        User,
        related_name='sent_friend_requests',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User,
        related_name='received_friend_requests',
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    class Meta:
        unique_together = ('sender', 'receiver')
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'receiver'],
                condition=models.Q(status='pending'),
                name='unique_pending_request'
            )
        ]
        verbose_name = 'Friend Request'
        verbose_name_plural = 'Friend Requests'

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"

    def accept(self):
        """
        Accept the friend request and create a Friendship.
        """
        if self.status == self.Status.PENDING:
            self.status = self.Status.ACCEPTED
            self.save()

            # Create Friendship
            Friendship.objects.create(user1=self.sender, user2=self.receiver)

    def reject(self):
        """
        Reject the friend request.
        """
        if self.status == self.Status.PENDING:
            self.status = self.Status.REJECTED
            self.save()


# Friendship model to manage active friendships
class Friendship(BaseModel):
    user1 = models.ForeignKey(
        User,
        related_name='friendships_initiated',
        on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        User,
        related_name='friendships_received',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user1', 'user2')
        constraints = [
            models.CheckConstraint(
                check=models.Q(user1__lt=models.F('user2')),
                name='user1_lt_user2'
            )
        ]
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username}"


# Block model to manage blocking between users
class Block(BaseModel):
    blocker = models.ForeignKey(
        User,
        related_name='blocks_initiated',
        on_delete=models.CASCADE
    )
    blocked = models.ForeignKey(
        User,
        related_name='blocked_by',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('blocker', 'blocked')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(blocker=models.F('blocked')),
                name='block_self_check'
            )
        ]
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"
