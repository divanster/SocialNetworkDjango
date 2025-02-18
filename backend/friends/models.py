from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import SoftDeleteModel, UUIDModel, BaseModel

# Get the custom User model
User = get_user_model()


# FriendRequest model to manage friend requests between users
class FriendRequest(SoftDeleteModel, UUIDModel, BaseModel):
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
        if self.status == self.Status.PENDING:
            # Ensure neither user is blocked
            if Block.objects.filter(
                    models.Q(blocker=self.sender, blocked=self.receiver) |
                    models.Q(blocker=self.receiver, blocked=self.sender)
            ).exists():
                raise ValidationError(
                    "Cannot accept a friend request involving blocked users.")

            self.status = self.Status.ACCEPTED
            self.save()

            if str(self.sender.id) < str(self.receiver.id):
                user1, user2 = self.sender, self.receiver
            else:
                user1, user2 = self.receiver, self.sender
            Friendship.objects.create(user1=user1, user2=user2)

    def reject(self):
        if self.status == self.Status.PENDING:
            self.status = self.Status.REJECTED
            self.save()


# Friendship model to manage active friendships
class Friendship(SoftDeleteModel, UUIDModel, BaseModel):
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
class Block(SoftDeleteModel, UUIDModel, BaseModel):
    blocker = models.ForeignKey(
        User,
        related_name='blocks_initiated',
        on_delete=models.CASCADE
    )
    blocked = models.ForeignKey(
        User,
        related_name='blocked_by',
        on_delete=models.CASCADE,
        null=True,  # Handle existing rows without this field
        blank=True
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
