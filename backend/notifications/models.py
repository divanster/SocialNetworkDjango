from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import UUIDModel, BaseModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

class Notification(UUIDModel, BaseModel):
    """
    Notification model for storing notification events.
    """
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('tag', 'Tag'),
        ('friend_request', 'Friend Request'),
        ('message', 'Message'),
        ('reaction', 'Reaction'),
        ('accepted_request', 'Accepted Friend Request'),
        ('post', 'New Post'),
        ('update', 'Profile Update'),
    )

    sender = models.ForeignKey(
        User,
        related_name='sent_notifications',
        on_delete=models.CASCADE,
        help_text="User sending the notification"
    )
    receiver = models.ForeignKey(
        User,
        related_name='received_notifications',
        on_delete=models.CASCADE,
        help_text="User receiving the notification"
    )
    notification_type = models.CharField(
        max_length=21,
        choices=NOTIFICATION_TYPES,
        default='like',
        help_text="Type of notification"
    )
    text = models.TextField(
        blank=True,
        help_text="Additional text for the notification"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates whether the notification has been read"
    )
    # Generic relation to any content type
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Content type of the related object"
    )
    object_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of the related object"
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver']),
            models.Index(fields=['sender', 'receiver']),
        ]

    def __str__(self):
        return f"{self.sender.username} sent a {self.get_notification_type_display()} notification to {self.receiver.username}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()
