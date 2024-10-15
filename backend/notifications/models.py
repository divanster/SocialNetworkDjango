# notifications/models.py

from django.db import models
from core.models.base_models import BaseModel

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
    sender_id = models.IntegerField()
    sender_username = models.CharField(max_length=150)
    receiver_id = models.IntegerField()
    receiver_username = models.CharField(max_length=150)
    notification_type = models.CharField(
        max_length=21,
        choices=NOTIFICATION_TYPES,
        default='like',
    )
    text = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    # Adjusted content_type and object_id fields
    content_type = models.CharField(max_length=100, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (f"{self.sender_username} sent a {self.get_notification_type_display()}"
                f" notification to {self.receiver_username}")

    def mark_as_read(self):
        """Helper method to mark the notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save()

    def get_content_object_url(self):
        """
        Helper method to get the URL of the related content object if it exists.
        Since we no longer have 'content_object', we need to implement this differently.
        """
        # Implement logic to construct the URL based on 'content_type' and 'object_id'
        # For example:
        if self.content_type and self.object_id:
            # Construct the URL based on content_type and object_id
            # This is a placeholder example
            return f"/{self.content_type.lower()}/{self.object_id}/"
        return None
