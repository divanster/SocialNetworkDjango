from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FriendRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    sender = models.ForeignKey(User, related_name='sent_friend_requests',
                               on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_friend_requests',
                                 on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.PENDING)

    class Meta:
        unique_together = ('sender', 'receiver')
        constraints = [
            models.UniqueConstraint(fields=['sender', 'receiver'],
                                    condition=models.Q(status='pending'),
                                    name='unique_pending_request')
        ]

    def clean(self):
        # Check if sender has blocked the receiver or vice versa
        if Block.objects.filter(blocker=self.sender, blocked=self.receiver).exists() or \
                Block.objects.filter(blocker=self.receiver,
                                     blocked=self.sender).exists():
            raise ValidationError(
                "Cannot send friend request. One of the users is blocked.")

    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method before saving to validate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"


class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name='friendships',
                              on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'],
                                    name='unique_friendship'),
            models.CheckConstraint(check=models.Q(user1__lt=models.F('user2')),
                                   name='user1_lt_user2'),
        ]

    def clean(self):
        # Check if either user has blocked the other
        if Block.objects.filter(blocker=self.user1, blocked=self.user2).exists() or \
                Block.objects.filter(blocker=self.user2, blocked=self.user1).exists():
            raise ValidationError(
                "Cannot create friendship. One of the users is blocked.")

    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method before saving to validate
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username}"


class Block(models.Model):
    blocker = models.ForeignKey(User, related_name='blocker_set',
                                on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_set',
                                on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')
        constraints = [
            models.CheckConstraint(check=~models.Q(blocker=models.F('blocked')),
                                   name='block_self_check')
        ]

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"
