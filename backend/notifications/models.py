from django.db import models
from core.models.base_models import BaseModel
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

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
    # Add more as needed
)


class Notification(BaseModel):
    sender = models.ForeignKey(
        User,
        related_name='sent_notifications',
        on_delete=models.CASCADE,
        help_text="The user who triggered the notification"
    )
    receiver = models.ForeignKey(
        User,
        related_name='received_notifications',
        on_delete=models.CASCADE,
        help_text="The user who receives the notification"
    )
    notification_type = models.CharField(
        max_length=21,  # Adjusted to fit the longest choice "accepted_request"
        choices=NOTIFICATION_TYPES,
        default='like',
        help_text="The type of notification"
    )
    text = models.TextField(blank=True, help_text="Optional custom notification message")
    is_read = models.BooleanField(default=False, help_text="Has the notification been read?")

    # Generic relation fields
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The content type of the related object"
    )
    object_id = models.UUIDField(null=True, blank=True, help_text="ID of the related object")
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']  # Default ordering by the latest notifications first
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.sender} sent a {self.get_notification_type_display()} notification to {self.receiver}"

    def mark_as_read(self):
        """Helper method to mark the notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save()

    def get_content_object_url(self):
        """Helper method to get the URL of the related content object if it exists."""
        if self.content_object and hasattr(self.content_object, 'get_absolute_url'):
            return self.content_object.get_absolute_url()
        return None
